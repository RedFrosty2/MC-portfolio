"""Process-local storage for the current recurring availability value."""

from odysseus.domain.availability import RecurringTrainingAvailability


class InMemoryTrainingAvailabilityStore:
    """Hold one immutable week and satisfy TrainingAvailabilityStore structurally.

    Construction requires an existing complete week. Values are retained
    directly, without copying or durable persistence, and each instance owns
    its current value.
    """

    def __init__(self, availability: RecurringTrainingAvailability) -> None:
        self._availability = availability

    def load(self) -> RecurringTrainingAvailability:
        """Return the currently held domain object without converting it."""
        return self._availability

    def save(self, availability: RecurringTrainingAvailability) -> None:
        """Replace this instance's current week with the supplied object."""
        self._availability = availability
