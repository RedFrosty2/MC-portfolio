from dataclasses import FrozenInstanceError

import pytest

from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)


@pytest.fixture
def complete_week() -> tuple[DailyTrainingAvailability, ...]:
    return tuple(
        DailyTrainingAvailability(
            weekday=weekday,
            am_available=True,
            pm_available=False,
            is_rest_day=False,
        )
        for weekday in Weekday
    )


def test_complete_monday_to_sunday_week_is_valid(
    complete_week: tuple[DailyTrainingAvailability, ...],
) -> None:
    availability = RecurringTrainingAvailability(days=complete_week)

    assert availability.days == complete_week
    assert tuple(day.weekday for day in availability.days) == (
        Weekday.MONDAY,
        Weekday.TUESDAY,
        Weekday.WEDNESDAY,
        Weekday.THURSDAY,
        Weekday.FRIDAY,
        Weekday.SATURDAY,
        Weekday.SUNDAY,
    )


@pytest.mark.parametrize(
    "am_available, pm_available", [(True, False), (False, True), (True, True)]
)
def test_am_and_pm_availability_are_independent(
    am_available: bool, pm_available: bool
) -> None:
    day = DailyTrainingAvailability(
        weekday=Weekday.MONDAY,
        am_available=am_available,
        pm_available=pm_available,
        is_rest_day=False,
    )

    assert day.am_available is am_available
    assert day.pm_available is pm_available


def test_entirely_unavailable_day_need_not_be_a_rest_day() -> None:
    day = DailyTrainingAvailability(
        weekday=Weekday.MONDAY,
        am_available=False,
        pm_available=False,
        is_rest_day=False,
    )

    assert not day.am_available
    assert not day.pm_available
    assert not day.is_rest_day


def test_explicit_rest_day_is_valid_without_training_availability() -> None:
    day = DailyTrainingAvailability(
        weekday=Weekday.SUNDAY,
        am_available=False,
        pm_available=False,
        is_rest_day=True,
    )

    assert day.is_rest_day
    assert not day.am_available
    assert not day.pm_available


@pytest.mark.parametrize(
    "am_available, pm_available", [(True, False), (False, True), (True, True)]
)
def test_rest_day_rejects_training_availability(
    am_available: bool, pm_available: bool
) -> None:
    with pytest.raises(ValueError, match="rest day"):
        DailyTrainingAvailability(
            weekday=Weekday.SUNDAY,
            am_available=am_available,
            pm_available=pm_available,
            is_rest_day=True,
        )


def test_recurring_week_rejects_a_missing_weekday(
    complete_week: tuple[DailyTrainingAvailability, ...],
) -> None:
    with pytest.raises(ValueError, match="each weekday exactly once"):
        RecurringTrainingAvailability(days=complete_week[:-1])


@pytest.mark.parametrize("append_duplicate", [False, True])
def test_recurring_week_rejects_a_duplicate_weekday(
    complete_week: tuple[DailyTrainingAvailability, ...], append_duplicate: bool
) -> None:
    days = complete_week if append_duplicate else complete_week[:-1]

    with pytest.raises(ValueError, match="each weekday exactly once"):
        RecurringTrainingAvailability(days=(*days, complete_week[0]))


def test_daily_availability_is_immutable(
    complete_week: tuple[DailyTrainingAvailability, ...],
) -> None:
    with pytest.raises(FrozenInstanceError):
        complete_week[0].am_available = False


def test_recurring_availability_is_immutable(
    complete_week: tuple[DailyTrainingAvailability, ...],
) -> None:
    availability = RecurringTrainingAvailability(days=complete_week)

    with pytest.raises(FrozenInstanceError):
        availability.days = ()
