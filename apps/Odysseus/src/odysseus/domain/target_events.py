"""Represent dated participation targets independently of their linked goals."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
from uuid import UUID


class TargetEventType(StrEnum):
    """Supported categories of real-world target events."""

    RUNNING = "running"
    HYROX = "hyrox"
    STRENGTH = "strength"
    OTHER = "other"


class TargetEventStatus(StrEnum):
    """Explicit event lifecycle states, separate from goal statuses."""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class TargetEvent:
    """An immutable dated event that may exist without any linked goals.

    The caller supplies its UUID and status. Past dates are valid and do not
    trigger status changes. The application owns effects on linked goals.

    Raises:
        ValueError: If the name is empty or whitespace-only.
    """

    id: UUID
    name: str
    event_date: date
    event_type: TargetEventType
    status: TargetEventStatus

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError(
                "A target event name must not be empty or whitespace-only."
            )
