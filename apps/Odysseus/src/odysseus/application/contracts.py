from typing import Protocol

from odysseus.domain.availability import RecurringTrainingAvailability


class TrainingAvailabilityStore(Protocol):
    def load(self) -> RecurringTrainingAvailability: ...

    def save(self, availability: RecurringTrainingAvailability) -> None: ...
