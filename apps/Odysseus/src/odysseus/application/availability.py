from odysseus.application.contracts import TrainingAvailabilityStore
from odysseus.domain.availability import RecurringTrainingAvailability


class TrainingAvailabilityUseCases:
    def __init__(self, store: TrainingAvailabilityStore) -> None:
        self._store = store

    def get_recurring_availability(self) -> RecurringTrainingAvailability:
        return self._store.load()

    def update_recurring_availability(
        self, availability: RecurringTrainingAvailability
    ) -> None:
        self._store.save(availability)
