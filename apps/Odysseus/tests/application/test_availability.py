from unittest.mock import create_autospec

import pytest

from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.application.contracts import TrainingAvailabilityStore
from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)


@pytest.fixture
def recurring_availability() -> RecurringTrainingAvailability:
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


def test_get_loads_through_store_contract_and_returns_the_exact_domain_value(
    recurring_availability: RecurringTrainingAvailability,
) -> None:
    store = create_autospec(TrainingAvailabilityStore, instance=True, spec_set=True)
    store.load.return_value = recurring_availability
    use_cases = TrainingAvailabilityUseCases(store=store)

    result = use_cases.get_recurring_availability()

    store.load.assert_called_once_with()
    assert result is recurring_availability
    store.save.assert_not_called()


def test_update_saves_the_supplied_domain_value_through_store_contract(
    recurring_availability: RecurringTrainingAvailability,
) -> None:
    store = create_autospec(TrainingAvailabilityStore, instance=True, spec_set=True)
    use_cases = TrainingAvailabilityUseCases(store=store)

    use_cases.update_recurring_availability(recurring_availability)

    store.save.assert_called_once_with(recurring_availability)
    assert store.save.call_args.args[0] is recurring_availability
    store.load.assert_not_called()
