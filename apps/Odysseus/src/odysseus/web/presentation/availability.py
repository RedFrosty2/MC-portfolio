from dataclasses import dataclass

from odysseus.domain.availability import RecurringTrainingAvailability, Weekday


@dataclass(frozen=True)
class TrainingAvailabilityDayView:
    weekday_label: str
    am_available: bool
    pm_available: bool
    is_rest_day: bool


@dataclass(frozen=True)
class TrainingAvailabilityView:
    days: tuple[TrainingAvailabilityDayView, ...]


def build_training_availability_view(
    availability: RecurringTrainingAvailability,
) -> TrainingAvailabilityView:
    days_by_weekday = {day.weekday: day for day in availability.days}
    return TrainingAvailabilityView(
        days=tuple(
            TrainingAvailabilityDayView(
                weekday_label=weekday.value.capitalize(),
                am_available=days_by_weekday[weekday].am_available,
                pm_available=days_by_weekday[weekday].pm_available,
                is_rest_day=days_by_weekday[weekday].is_rest_day,
            )
            for weekday in Weekday
        )
    )
