"""Retrieve and replace recurring availability through an application contract."""

from odysseus.application.contracts import TrainingAvailabilityStore
from odysseus.domain.availability import RecurringTrainingAvailability


class TrainingAvailabilityUseCases:
    """Delegate complete weekly availability values to the injected store.

    Domain construction owns validity; this boundary neither repeats those
    checks nor depends on a concrete storage adapter.
    """

    def __init__(self, store: TrainingAvailabilityStore) -> None:
        self._store = store

    def get_recurring_availability(self) -> RecurringTrainingAvailability:
        """Return the exact domain value loaded from the store."""
        return self._store.load()

    def update_recurring_availability(
        self, availability: RecurringTrainingAvailability
    ) -> None:
        """Save the supplied complete week, replacing the previous value."""
        self._store.save(availability)
