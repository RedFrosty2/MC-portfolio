"""Process-local storage of complete application goal/event snapshots."""

from odysseus.application.contracts import GoalsAndEventsSnapshot


class InMemoryGoalsAndEventsStore:
    """Hold one snapshot and satisfy GoalsAndEventsStore structurally.

    An omitted initial snapshot starts empty for this instance; a supplied
    snapshot is retained directly, preserving domain objects and UUIDs. Storage
    neither persists beyond the process nor performs relationship/lifecycle rules.
    """

    def __init__(self, snapshot: GoalsAndEventsSnapshot | None = None) -> None:
        self._snapshot = GoalsAndEventsSnapshot() if snapshot is None else snapshot

    def load(self) -> GoalsAndEventsSnapshot:
        """Return the current snapshot object without copying its contents."""
        return self._snapshot

    def save(self, snapshot: GoalsAndEventsSnapshot) -> None:
        """Replace the entire current snapshot without merging collections."""
        self._snapshot = snapshot
