from dataclasses import dataclass
from enum import StrEnum


class Weekday(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


@dataclass(frozen=True)
class DailyTrainingAvailability:
    weekday: Weekday
    am_available: bool
    pm_available: bool
    is_rest_day: bool

    def __post_init__(self) -> None:
        if self.is_rest_day and (self.am_available or self.pm_available):
            raise ValueError("A rest day cannot have AM or PM availability.")


@dataclass(frozen=True)
class RecurringTrainingAvailability:
    days: tuple[DailyTrainingAvailability, ...]

    def __post_init__(self) -> None:
        weekdays = {day.weekday for day in self.days}
        if len(self.days) != len(Weekday) or weekdays != set(Weekday):
            raise ValueError("A recurring week must contain each weekday exactly once.")
