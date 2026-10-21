"""Coordinate stored goals and events and select future preparation targets."""

from dataclasses import dataclass, replace
from datetime import date
from uuid import UUID, uuid4

from odysseus.application.contracts import GoalsAndEventsStore
from odysseus.domain.goals import Goal, GoalStatus
from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)


@dataclass(frozen=True)
class FuturePlanningTargets:
    """A read-only selection retaining the original immutable domain objects.

    Attributes:
        goals: Selected goals in their stored order.
        target_events: Selected target events in their stored order.
    """

    goals: tuple[Goal, ...]
    target_events: tuple[TargetEvent, ...]


class GoalsAndEventsUseCases:
    """Coordinate snapshot storage, goal/event relationships, and target selection.

    The application-owned store supplies snapshots. Mutations save replacement
    snapshots, including coordinated cancellation and unlinking changes; queries
    leave stored records untouched. Domain constructors own field validity.
    """

    def __init__(self, store: GoalsAndEventsStore) -> None:
        self._store = store

    def get_future_planning_targets(self, as_of: date) -> FuturePlanningTargets:
        """Select active preparation targets from one snapshot without saving.

        Goals must be ACTIVE and undated or due on/after the cutoff. Linked
        goals also require an existing ACTIVE event dated on/after the cutoff.
        Historical records and their statuses remain unchanged.

        Args:
            as_of: Inclusive date cutoff supplied by the caller; no system
                clock is consulted.

        Returns:
            Selected goals and events in their respective stored orders, using
            the original domain objects. Events must be ACTIVE and dated on or
            after the cutoff; missing event references exclude linked goals.
        """
        snapshot = self._store.load()
        target_events = tuple(
            event
            for event in snapshot.target_events
            if event.status == TargetEventStatus.ACTIVE and event.event_date >= as_of
        )
        target_event_ids = {event.id for event in target_events}
        goals = tuple(
            goal
            for goal in snapshot.goals
            if goal.status == GoalStatus.ACTIVE
            and (goal.target_date is None or goal.target_date >= as_of)
            and (
                goal.target_event_id is None or goal.target_event_id in target_event_ids
            )
        )
        return FuturePlanningTargets(goals=goals, target_events=target_events)

    def list_goals(self) -> tuple[Goal, ...]:
        """Return all stored goals in order, including non-active and past goals."""
        return self._store.load().goals

    def get_goal(self, goal_id: UUID) -> Goal:
        """Return the stored goal regardless of its date or status.

        Raises:
            LookupError: If no stored goal has the supplied ID.
        """
        snapshot = self._store.load()
        for goal in snapshot.goals:
            if goal.id == goal_id:
                return goal
        raise LookupError(f"Goal {goal_id} does not exist.")

    def create_goal(
        self,
        *,
        title: str,
        status: GoalStatus,
        target_date: date | None = None,
        target_event_id: UUID | None = None,
    ) -> Goal:
        """Assign a UUID and save a new goal alongside the existing records.

        Args:
            title: Desired outcome, validated by the domain constructor.
            status: Explicit initial status; dates do not alter it.
            target_date: Optional target date, which may be historical.
            target_event_id: Optional reference to an existing event. ACTIVE
                goals cannot reference a CANCELLED event.

        Returns:
            The new immutable goal, with its application-generated UUID.

        Raises:
            LookupError: If the referenced event does not exist.
            ValueError: If the title is blank or an ACTIVE goal references a
                CANCELLED event. No snapshot is saved on validation failure.
        """
        snapshot = self._store.load()
        if target_event_id is not None and not any(
            event.id == target_event_id for event in snapshot.target_events
        ):
            raise LookupError(f"Target event {target_event_id} does not exist.")
        if status == GoalStatus.ACTIVE and any(
            event.id == target_event_id and event.status == TargetEventStatus.CANCELLED
            for event in snapshot.target_events
        ):
            raise ValueError(
                "Cannot link an active goal to cancelled target event "
                f"{target_event_id}."
            )

        goal = Goal(
            id=uuid4(),
            title=title,
            status=status,
            target_date=target_date,
            target_event_id=target_event_id,
        )
        self._store.save(replace(snapshot, goals=(*snapshot.goals, goal)))
        return goal

    def update_goal(self, goal: Goal) -> None:
        """Replace an existing goal while leaving events and other goals intact.

        The supplied domain value is a complete replacement with an existing
        ID, so its status, optional date, and event link are explicit choices.

        Raises:
            LookupError: If the goal or its referenced event does not exist.
            ValueError: If an ACTIVE goal references a CANCELLED event.
                Rejected updates do not save.
        """
        snapshot = self._store.load()
        if not any(existing.id == goal.id for existing in snapshot.goals):
            raise LookupError(f"Goal {goal.id} does not exist.")
        if goal.target_event_id is not None and not any(
            event.id == goal.target_event_id for event in snapshot.target_events
        ):
            raise LookupError(f"Target event {goal.target_event_id} does not exist.")
        if goal.status == GoalStatus.ACTIVE and any(
            event.id == goal.target_event_id
            and event.status == TargetEventStatus.CANCELLED
            for event in snapshot.target_events
        ):
            raise ValueError(
                "Cannot link an active goal to cancelled target event "
                f"{goal.target_event_id}."
            )

        self._store.save(
            replace(
                snapshot,
                goals=tuple(
                    goal if existing.id == goal.id else existing
                    for existing in snapshot.goals
                ),
            )
        )

    def delete_goal(self, goal_id: UUID) -> None:
        """Remove one goal without changing its event or peer goals.

        Raises:
            LookupError: If the goal does not exist; nothing is saved.
        """
        snapshot = self._store.load()
        if not any(goal.id == goal_id for goal in snapshot.goals):
            raise LookupError(f"Goal {goal_id} does not exist.")

        self._store.save(
            replace(
                snapshot,
                goals=tuple(goal for goal in snapshot.goals if goal.id != goal_id),
            )
        )

    def list_target_events(self) -> tuple[TargetEvent, ...]:
        """Return all stored events in order, including historical records."""
        return self._store.load().target_events

    def get_target_event(self, event_id: UUID) -> TargetEvent:
        """Return the stored event regardless of its date or status.

        Raises:
            LookupError: If no stored event has the supplied ID.
        """
        snapshot = self._store.load()
        for event in snapshot.target_events:
            if event.id == event_id:
                return event
        raise LookupError(f"Target event {event_id} does not exist.")

    def create_target_event(
        self,
        *,
        name: str,
        event_date: date,
        event_type: TargetEventType,
        status: TargetEventStatus,
    ) -> TargetEvent:
        """Assign a UUID and save a new event without requiring linked goals.

        Dates may be historical; the supplied type and status are preserved.
        The domain constructor validates the name before anything is saved.

        Returns:
            The new immutable event, with its application-generated UUID.

        Raises:
            ValueError: If the event name is empty or whitespace-only.
        """
        snapshot = self._store.load()
        event = TargetEvent(
            id=uuid4(),
            name=name,
            event_date=event_date,
            event_type=event_type,
            status=status,
        )
        self._store.save(
            replace(snapshot, target_events=(*snapshot.target_events, event))
        )
        return event

    def update_target_event(self, event: TargetEvent) -> None:
        """Replace an event and coordinate cancellation in a single snapshot save.

        Setting CANCELLED also cancels its ACTIVE linked goals, retaining all
        other goal fields and links. Other goal statuses and unrelated goals
        stay unchanged. Reactivating an event does not reactivate its goals;
        COMPLETED and INACTIVE event updates do not cancel them.

        Raises:
            LookupError: If the event does not exist; nothing is saved.
        """
        snapshot = self._store.load()
        if not any(existing.id == event.id for existing in snapshot.target_events):
            raise LookupError(f"Target event {event.id} does not exist.")

        # Event cancellation must not rewrite completed history or other goal states.
        self._store.save(
            replace(
                snapshot,
                goals=tuple(
                    replace(goal, status=GoalStatus.CANCELLED)
                    if event.status == TargetEventStatus.CANCELLED
                    and goal.target_event_id == event.id
                    and goal.status == GoalStatus.ACTIVE
                    else goal
                    for goal in snapshot.goals
                ),
                target_events=tuple(
                    event if existing.id == event.id else existing
                    for existing in snapshot.target_events
                ),
            )
        )

    def delete_target_event(self, event_id: UUID) -> None:
        """Remove an event and unlink its goals in one replacement snapshot.

        Goals remain stored with all other fields, including status and target
        date, unchanged. Deletion does not apply cancellation rules.

        Raises:
            LookupError: If the event does not exist; nothing is saved.
        """
        snapshot = self._store.load()
        if not any(event.id == event_id for event in snapshot.target_events):
            raise LookupError(f"Target event {event_id} does not exist.")

        # Separate saves could expose goals referencing an event already removed.
        self._store.save(
            replace(
                snapshot,
                goals=tuple(
                    replace(goal, target_event_id=None)
                    if goal.target_event_id == event_id
                    else goal
                    for goal in snapshot.goals
                ),
                target_events=tuple(
                    event for event in snapshot.target_events if event.id != event_id
                ),
            )
        )
