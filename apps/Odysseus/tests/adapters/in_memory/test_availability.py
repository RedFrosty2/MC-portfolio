import pytest

from odysseus.adapters.in_memory.availability import InMemoryTrainingAvailabilityStore
from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.application.contracts import TrainingAvailabilityStore
from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)


@pytest.fixture
def initial_availability() -> RecurringTrainingAvailability:
    return RecurringTrainingAvailability(
        days=tuple(
            DailyTrainingAvailability(
                weekday=weekday,
                am_available=True,
                pm_available=False,
                is_rest_day=False,
            )
            for weekday in Weekday
        )
    )


@pytest.fixture
def replacement_availability() -> RecurringTrainingAvailability:
    return RecurringTrainingAvailability(
        days=tuple(
            DailyTrainingAvailability(
                weekday=weekday,
                am_available=False,
                pm_available=True,
                is_rest_day=False,
            )
            for weekday in Weekday
        )
    )


def test_load_returns_the_initial_domain_value(
    initial_availability: RecurringTrainingAvailability,
) -> None:
    store = InMemoryTrainingAvailabilityStore(availability=initial_availability)

    assert store.load() is initial_availability


def test_save_replaces_the_value_returned_by_subsequent_loads(
    initial_availability: RecurringTrainingAvailability,
    replacement_availability: RecurringTrainingAvailability,
) -> None:
    store = InMemoryTrainingAvailabilityStore(availability=initial_availability)

    store.save(replacement_availability)

    assert store.load() is replacement_availability


def test_store_supports_retrieval_and_update_through_application_use_cases(
    initial_availability: RecurringTrainingAvailability,
    replacement_availability: RecurringTrainingAvailability,
) -> None:
    store: TrainingAvailabilityStore = InMemoryTrainingAvailabilityStore(
        availability=initial_availability
    )
    use_cases = TrainingAvailabilityUseCases(store=store)

    assert use_cases.get_recurring_availability() is initial_availability

    use_cases.update_recurring_availability(replacement_availability)

    assert use_cases.get_recurring_availability() is replacement_availability
    assert store.load() is replacement_availability
