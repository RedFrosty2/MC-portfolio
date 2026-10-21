"""Prepare recurring availability for rendering without HTTP or storage work."""

from dataclasses import dataclass

from odysseus.domain.availability import RecurringTrainingAvailability, Weekday


@dataclass(frozen=True)
class TrainingAvailabilityDayView:
    """Immutable display label and unchanged availability flags for one weekday."""

    weekday_label: str
    am_available: bool
    pm_available: bool
    is_rest_day: bool


@dataclass(frozen=True)
class TrainingAvailabilityView:
    """Immutable day rows prepared for rendering by the availability builder."""

    days: tuple[TrainingAvailabilityDayView, ...]


def build_training_availability_view(
    availability: RecurringTrainingAvailability,
) -> TrainingAvailabilityView:
    """Build seven display rows in Monday-to-Sunday order from a valid week.

    The domain value may be stored in any order. Labels are human-readable;
    flags are copied unchanged so ordinary unavailability stays distinct from
    explicit rest. This translation does not repeat domain validation.

    Args:
        availability: The complete week returned by the application.

    Returns:
        An immutable View with one row per weekday in display order.
    """
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
