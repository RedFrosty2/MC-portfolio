"""Translate supplied goals and events into display values without filtering."""

from dataclasses import dataclass
from uuid import UUID

from odysseus.domain.goals import Goal
from odysseus.domain.target_events import TargetEvent, TargetEventType


@dataclass(frozen=True)
class GoalRowView:
    """Immutable goal display values retaining the record UUID.

    A None linked-event label means standalone. An unresolved reference has
    an explicit text label so it cannot be mistaken for an absent link.
    """

    id: UUID
    title: str
    status_label: str
    target_date_label: str
    linked_event_label: str | None


@dataclass(frozen=True)
class TargetEventRowView:
    """Immutable event labels and required date, retaining the record UUID."""

    id: UUID
    name: str
    event_type_label: str
    event_date_label: str
    status_label: str


@dataclass(frozen=True)
class GoalsAndEventsView:
    """Immutable goal and event rows in their respective supplied orders."""

    goals: tuple[GoalRowView, ...]
    target_events: tuple[TargetEventRowView, ...]


def build_goals_and_events_view(
    goals: tuple[Goal, ...],
    target_events: tuple[TargetEvent, ...],
) -> GoalsAndEventsView:
    """Translate all supplied records without storage, HTTP, or lifecycle work.

    Args:
        goals: Domain goals in display order, including historical records.
        target_events: Domain events in display order, also used to resolve
            goal references by UUID.

    Returns:
        Immutable rows preserving IDs, text, status meaning, and supplied order.
        Dates use DD Mon YYYY, such as 01 May 2030. A goal's own date takes
        precedence; otherwise a resolved link supplies "Event date: DD Mon YYYY".
        Undated standalone goals show "No deadline", while undated goals with
        missing events show "Event date unavailable". Standalone event labels
        are None; missing links show "Unresolved event reference". No record is
        hidden or mutated.
    """
    events_by_id = {event.id: event for event in target_events}
    goal_rows: list[GoalRowView] = []
    for goal in goals:
        linked_event_label: str | None
        if goal.target_event_id is None:
            linked_event_label = None
        elif goal.target_event_id in events_by_id:
            linked_event_label = events_by_id[goal.target_event_id].name
        else:
            linked_event_label = "Unresolved event reference"

        if goal.target_date is not None:
            target_date_label = goal.target_date.strftime("%d %b %Y")
        elif goal.target_event_id is None:
            target_date_label = "No deadline"
        elif goal.target_event_id in events_by_id:
            event_date = events_by_id[goal.target_event_id].event_date
            target_date_label = f"Event date: {event_date:%d %b %Y}"
        else:
            target_date_label = "Event date unavailable"

        goal_rows.append(
            GoalRowView(
                id=goal.id,
                title=goal.title,
                status_label=goal.status.value.capitalize(),
                target_date_label=target_date_label,
                linked_event_label=linked_event_label,
            )
        )

    event_type_labels = {
        TargetEventType.RUNNING: "Running",
        TargetEventType.HYROX: "HYROX",
        TargetEventType.STRENGTH: "Strength",
        TargetEventType.OTHER: "Other",
    }
    return GoalsAndEventsView(
        goals=tuple(goal_rows),
        target_events=tuple(
            TargetEventRowView(
                id=event.id,
                name=event.name,
                event_type_label=event_type_labels[event.event_type],
                event_date_label=event.event_date.strftime("%d %b %Y"),
                status_label=event.status.value.capitalize(),
            )
            for event in target_events
        ),
    )
