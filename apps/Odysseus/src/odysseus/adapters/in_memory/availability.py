from odysseus.domain.availability import RecurringTrainingAvailability


class InMemoryTrainingAvailabilityStore:
    def __init__(self, availability: RecurringTrainingAvailability) -> None:
        self._availability = availability

    def load(self) -> RecurringTrainingAvailability:
        return self._availability

    def save(self, availability: RecurringTrainingAvailability) -> None:
        self._availability = availability
