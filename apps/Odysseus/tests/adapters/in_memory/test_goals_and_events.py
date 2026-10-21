from dataclasses import replace
from datetime import date
from uuid import UUID

import pytest

from odysseus.adapters.in_memory.goals_and_events import InMemoryGoalsAndEventsStore
from odysseus.application.contracts import GoalsAndEventsSnapshot, GoalsAndEventsStore
from odysseus.application.goals_and_events import GoalsAndEventsUseCases
from odysseus.domain.goals import Goal, GoalStatus
from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)


@pytest.fixture
def initial_snapshot() -> GoalsAndEventsSnapshot:
    event = TargetEvent(
        id=UUID(int=1),
        name="Historical race",
        event_date=date(2000, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.COMPLETED,
    )
    goal = Goal(
        id=UUID(int=2),
        title="Finish the race",
        status=GoalStatus.COMPLETED,
        target_date=date(2000, 5, 1),
        target_event_id=event.id,
    )
    return GoalsAndEventsSnapshot(goals=(goal,), target_events=(event,))


@pytest.fixture
def replacement_snapshot(
    initial_snapshot: GoalsAndEventsSnapshot,
) -> GoalsAndEventsSnapshot:
    event = replace(
        initial_snapshot.target_events[0],
        id=UUID(int=3),
        name="HYROX race",
        event_date=date(2030, 6, 1),
        event_type=TargetEventType.HYROX,
        status=TargetEventStatus.ACTIVE,
    )
    goal = replace(
        initial_snapshot.goals[0],
        id=UUID(int=4),
        title="Complete HYROX",
        status=GoalStatus.INACTIVE,
        target_date=date(2030, 6, 1),
        target_event_id=event.id,
    )
    return GoalsAndEventsSnapshot(goals=(goal,), target_events=(event,))


def test_store_starts_with_an_empty_snapshot() -> None:
    store = InMemoryGoalsAndEventsStore()

    assert store.load() == GoalsAndEventsSnapshot()


def test_load_returns_the_supplied_initial_snapshot(
    initial_snapshot: GoalsAndEventsSnapshot,
) -> None:
    store = InMemoryGoalsAndEventsStore(snapshot=initial_snapshot)

    assert store.load() is initial_snapshot


def test_load_preserves_domain_objects_and_their_uuids(
    initial_snapshot: GoalsAndEventsSnapshot,
) -> None:
    store = InMemoryGoalsAndEventsStore(snapshot=initial_snapshot)

    loaded = store.load()

    assert loaded.goals[0] is initial_snapshot.goals[0]
    assert loaded.target_events[0] is initial_snapshot.target_events[0]
    assert loaded.goals[0].id == UUID(int=2)
    assert loaded.target_events[0].id == UUID(int=1)
    assert loaded.goals[0].target_event_id == loaded.target_events[0].id


def test_save_replaces_rather_than_merges_the_current_snapshot(
    initial_snapshot: GoalsAndEventsSnapshot,
    replacement_snapshot: GoalsAndEventsSnapshot,
) -> None:
    store = InMemoryGoalsAndEventsStore(snapshot=initial_snapshot)

    store.save(replacement_snapshot)
    loaded = store.load()

    assert loaded is replacement_snapshot
    assert loaded.goals == replacement_snapshot.goals
    assert loaded.target_events == replacement_snapshot.target_events
    assert loaded.goals[0] is replacement_snapshot.goals[0]
    assert loaded.target_events[0] is replacement_snapshot.target_events[0]


def test_saving_an_empty_snapshot_removes_all_previously_stored_values(
    initial_snapshot: GoalsAndEventsSnapshot,
) -> None:
    store = InMemoryGoalsAndEventsStore(snapshot=initial_snapshot)
    empty_snapshot = GoalsAndEventsSnapshot()

    store.save(empty_snapshot)

    assert store.load() is empty_snapshot


def test_store_instances_keep_independent_snapshots(
    initial_snapshot: GoalsAndEventsSnapshot,
) -> None:
    first_store = InMemoryGoalsAndEventsStore()
    second_store = InMemoryGoalsAndEventsStore()

    first_store.save(initial_snapshot)

    assert first_store.load() is initial_snapshot
    assert second_store.load() == GoalsAndEventsSnapshot()


def test_use_cases_retain_and_unlink_goals_after_deleting_their_event() -> None:
    store: GoalsAndEventsStore = InMemoryGoalsAndEventsStore()
    use_cases = GoalsAndEventsUseCases(store)
    event = use_cases.create_target_event(
        name="Half marathon",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )
    first_goal = use_cases.create_goal(
        title="Finish the race",
        status=GoalStatus.ACTIVE,
        target_date=date(2030, 5, 1),
        target_event_id=event.id,
    )
    second_goal = use_cases.create_goal(
        title="Improve race pace",
        status=GoalStatus.INACTIVE,
        target_date=date(2000, 5, 1),
        target_event_id=event.id,
    )

    assert use_cases.list_target_events() == (event,)
    assert use_cases.list_goals() == (first_goal, second_goal)

    use_cases.delete_target_event(event.id)

    expected_goals = (
        replace(first_goal, target_event_id=None),
        replace(second_goal, target_event_id=None),
    )
    assert use_cases.list_target_events() == ()
    assert use_cases.list_goals() == expected_goals
    assert use_cases.get_goal(first_goal.id) == expected_goals[0]
    assert use_cases.get_goal(second_goal.id) == expected_goals[1]
    assert store.load() == GoalsAndEventsSnapshot(goals=expected_goals)
