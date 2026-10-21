"""Define recurring training opportunities and explicit rest constraints."""

from dataclasses import dataclass
from enum import StrEnum


class Weekday(StrEnum):
    """Weekdays declared in Monday-to-Sunday order with lowercase values."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass(frozen=True)
class DailyTrainingAvailability:
    """An immutable day's AM/PM opportunities and explicit rest designation.

    Explicit rest cannot coexist with AM or PM availability. All three flags
    may be false, representing ordinary unavailability rather than rest.

    Raises:
        ValueError: If an explicit rest day also has training availability.
    """

    weekday: Weekday
    am_available: bool
    pm_available: bool
    is_rest_day: bool

    def __post_init__(self) -> None:
        if self.is_rest_day and (self.am_available or self.pm_available):
            raise ValueError("A rest day cannot have AM or PM availability.")


@dataclass(frozen=True)
class RecurringTrainingAvailability:
    """A complete immutable week containing each weekday exactly once.

    The supplied tuple order is retained; presentation owns display ordering.

    Raises:
        ValueError: If weekdays are missing or duplicated.
    """

    days: tuple[DailyTrainingAvailability, ...]

    def __post_init__(self) -> None:
        weekdays = {day.weekday for day in self.days}
        if len(self.days) != len(Weekday) or weekdays != set(Weekday):
            raise ValueError("A recurring week must contain each weekday exactly once.")
