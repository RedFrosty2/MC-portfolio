import pytest

from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)
from odysseus.web.presentation.availability import (
    TrainingAvailabilityDayView,
    TrainingAvailabilityView,
    build_training_availability_view,
)


@pytest.fixture
def unordered_availability() -> RecurringTrainingAvailability:
    return RecurringTrainingAvailability(
        days=(
            DailyTrainingAvailability(Weekday.WEDNESDAY, True, True, False),
            DailyTrainingAvailability(Weekday.MONDAY, True, False, False),
            DailyTrainingAvailability(Weekday.SUNDAY, False, False, True),
            DailyTrainingAvailability(Weekday.FRIDAY, False, False, True),
            DailyTrainingAvailability(Weekday.TUESDAY, False, True, False),
            DailyTrainingAvailability(Weekday.SATURDAY, False, True, False),
            DailyTrainingAvailability(Weekday.THURSDAY, False, False, False),
        )
    )


def test_domain_week_is_converted_into_seven_day_views(
    unordered_availability: RecurringTrainingAvailability,
) -> None:
    view = build_training_availability_view(unordered_availability)

    assert isinstance(view, TrainingAvailabilityView)
    assert isinstance(view.days, tuple)
    assert len(view.days) == 7
    assert all(isinstance(day, TrainingAvailabilityDayView) for day in view.days)


def test_unordered_week_has_human_readable_labels_in_monday_to_sunday_order(
    unordered_availability: RecurringTrainingAvailability,
) -> None:
    view = build_training_availability_view(unordered_availability)

    assert tuple(day.weekday_label for day in view.days) == (
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    )


def test_am_pm_rest_and_ordinary_unavailability_are_preserved(
    unordered_availability: RecurringTrainingAvailability,
) -> None:
    view = build_training_availability_view(unordered_availability)

    assert {
        day.weekday_label: (day.am_available, day.pm_available, day.is_rest_day)
        for day in view.days
    } == {
        "Monday": (True, False, False),
        "Tuesday": (False, True, False),
        "Wednesday": (True, True, False),
        "Thursday": (False, False, False),
        "Friday": (False, False, True),
        "Saturday": (False, True, False),
        "Sunday": (False, False, True),
    }
