"""Represent athlete outcomes without storage or event-lifecycle coordination."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID


class GoalStatus(StrEnum):
    """Explicit goal lifecycle states, separate from target-event statuses."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class Goal:
    """An immutable desired outcome with an optional date and event reference.

    The caller supplies the UUID. Goals may stand alone, and historical target
    dates are valid without changing status. The application validates event
    references and coordinates their lifecycle; this model does not resolve IDs.

    Raises:
        ValueError: If the title is empty or whitespace-only.
    """

    id: UUID
    title: str
    status: GoalStatus
    target_date: date | None = None
    target_event_id: UUID | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("A goal title must not be empty or whitespace-only.")
