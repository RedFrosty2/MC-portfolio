"""Application-owned storage capabilities and coordinated goal/event state."""

from dataclasses import dataclass
from typing import Protocol

from odysseus.domain.availability import RecurringTrainingAvailability
from odysseus.domain.goals import Goal
from odysseus.domain.target_events import TargetEvent


class TrainingAvailabilityStore(Protocol):
    """Synchronous storage capability required by the availability use case."""

    def load(self) -> RecurringTrainingAvailability:
        """Return the current complete recurring availability value."""
        ...

    def save(self, availability: RecurringTrainingAvailability) -> None:
        """Replace the stored week with the supplied domain value."""
        ...


@dataclass(frozen=True)
class GoalsAndEventsSnapshot:
    """Immutable state allowing related goal and event changes to be saved together.

    Attributes:
        goals: Stored domain goals, including historical records, in stored order.
        target_events: Stored domain events in stored order, including history.
    """

    goals: tuple[Goal, ...] = ()
    target_events: tuple[TargetEvent, ...] = ()


class GoalsAndEventsStore(Protocol):
    """Synchronous storage of the whole goal/event state for each operation."""

    def load(self) -> GoalsAndEventsSnapshot:
        """Return the current goals and events, including historical records."""
        ...

    def save(self, snapshot: GoalsAndEventsSnapshot) -> None:
        """Replace both collections together with the supplied snapshot."""
        ...
