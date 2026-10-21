from dataclasses import FrozenInstanceError, replace
from datetime import date
from unittest.mock import Mock
from uuid import UUID

import pytest

from odysseus.application.contracts import GoalsAndEventsSnapshot, GoalsAndEventsStore
from odysseus.application.goals_and_events import GoalsAndEventsUseCases
from odysseus.domain.goals import Goal, GoalStatus
from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)


@pytest.fixture
def snapshot() -> GoalsAndEventsSnapshot:
    event = TargetEvent(
        id=UUID(int=1),
        name="Half marathon",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )
    other_event = replace(event, id=UUID(int=2), name="Another race")
    first_goal = Goal(
        id=UUID(int=3),
        title="Finish the race",
        status=GoalStatus.COMPLETED,
        target_date=date(2000, 5, 1),
        target_event_id=event.id,
    )
    second_goal = Goal(
        id=UUID(int=4),
        title="Improve race pace",
        status=GoalStatus.CANCELLED,
        target_date=date(2030, 4, 1),
        target_event_id=event.id,
    )
    standalone_goal = Goal(
        id=UUID(int=5), title="Build strength", status=GoalStatus.INACTIVE
    )
    return GoalsAndEventsSnapshot(
        goals=(first_goal, second_goal, standalone_goal),
        target_events=(event, other_event),
    )


@pytest.fixture
def store(snapshot: GoalsAndEventsSnapshot) -> Mock:
    store = Mock(spec=GoalsAndEventsStore)
    store.load.return_value = snapshot
    return store


@pytest.fixture
def cancellation_snapshot(snapshot: GoalsAndEventsSnapshot) -> GoalsAndEventsSnapshot:
    first_active_goal = replace(
        snapshot.goals[0], id=UUID(int=10), status=GoalStatus.ACTIVE
    )
    second_active_goal = replace(first_active_goal, id=UUID(int=11))
    inactive_goal = replace(
        snapshot.goals[0], id=UUID(int=12), status=GoalStatus.INACTIVE
    )
    other_event_goal = replace(
        first_active_goal,
        id=UUID(int=13),
        target_event_id=snapshot.target_events[1].id,
    )
    standalone_goal = replace(snapshot.goals[2], status=GoalStatus.ACTIVE)
    return replace(
        snapshot,
        goals=(
            first_active_goal,
            second_active_goal,
            snapshot.goals[0],
            inactive_goal,
            snapshot.goals[1],
            other_event_goal,
            standalone_goal,
        ),
    )


def test_snapshot_is_immutable_and_defaults_to_empty_tuples() -> None:
    snapshot = GoalsAndEventsSnapshot()

    assert snapshot.goals == ()
    assert snapshot.target_events == ()
    with pytest.raises(FrozenInstanceError):
        snapshot.goals = ()


def test_list_goals_returns_the_stored_domain_values(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    assert use_cases.list_goals() is snapshot.goals
    store.load.assert_called_once_with()
    store.save.assert_not_called()


def test_get_goal_returns_the_matching_domain_value(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    assert use_cases.get_goal(snapshot.goals[1].id) is snapshot.goals[1]
    store.load.assert_called_once_with()
    store.save.assert_not_called()


def test_list_target_events_returns_the_stored_domain_values(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    assert use_cases.list_target_events() is snapshot.target_events
    store.load.assert_called_once_with()
    store.save.assert_not_called()


def test_get_target_event_returns_the_matching_domain_value(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    assert (
        use_cases.get_target_event(snapshot.target_events[1].id)
        is (snapshot.target_events[1])
    )
    store.load.assert_called_once_with()
    store.save.assert_not_called()


@pytest.mark.parametrize("target_event_id", [None, UUID(int=1)])
def test_create_goal_saves_and_returns_a_new_goal_with_optional_event_linkage(
    store: Mock,
    snapshot: GoalsAndEventsSnapshot,
    target_event_id: UUID | None,
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    goal = use_cases.create_goal(
        title="Improve endurance",
        status=GoalStatus.CANCELLED,
        target_date=date(2000, 5, 1),
        target_event_id=target_event_id,
    )

    assert isinstance(goal.id, UUID)
    assert goal.id.version == 4
    assert goal.title == "Improve endurance"
    assert goal.status is GoalStatus.CANCELLED
    assert goal.target_date == date(2000, 5, 1)
    assert goal.target_event_id == target_event_id
    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        replace(snapshot, goals=(*snapshot.goals, goal)),
    )


def test_create_goal_without_optional_fields_saves_a_standalone_goal(
    store: Mock,
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    goal = use_cases.create_goal(title="Build endurance", status=GoalStatus.ACTIVE)

    assert goal.target_date is None
    assert goal.target_event_id is None
    store.save.assert_called_once()


def test_create_target_event_saves_and_returns_a_new_event(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    event = use_cases.create_target_event(
        name="Historical HYROX race",
        event_date=date(2000, 5, 1),
        event_type=TargetEventType.HYROX,
        status=TargetEventStatus.ACTIVE,
    )

    assert isinstance(event.id, UUID)
    assert event.id.version == 4
    assert event.name == "Historical HYROX race"
    assert event.event_date == date(2000, 5, 1)
    assert event.event_type is TargetEventType.HYROX
    assert event.status is TargetEventStatus.ACTIVE
    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        replace(snapshot, target_events=(*snapshot.target_events, event))
    )


def test_creation_assigns_distinct_uuid_identities(store: Mock) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    first_goal = use_cases.create_goal(title="Goal", status=GoalStatus.ACTIVE)
    second_goal = use_cases.create_goal(title="Goal", status=GoalStatus.ACTIVE)
    first_event = use_cases.create_target_event(
        name="Race",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )
    second_event = use_cases.create_target_event(
        name="Race",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )

    ids = {first_goal.id, second_goal.id, first_event.id, second_event.id}
    assert len(ids) == 4
    assert all(
        isinstance(entity_id, UUID) and entity_id.version == 4 for entity_id in ids
    )


@pytest.mark.parametrize("target_event_id", [None, UUID(int=1), UUID(int=2)])
def test_update_goal_replaces_only_the_matching_goal_and_preserves_its_id(
    store: Mock,
    snapshot: GoalsAndEventsSnapshot,
    target_event_id: UUID | None,
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    updated = replace(
        snapshot.goals[0],
        title="Updated goal",
        status=GoalStatus.INACTIVE,
        target_date=date(2001, 1, 1),
        target_event_id=target_event_id,
    )

    use_cases.update_goal(updated)

    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        replace(snapshot, goals=(updated, *snapshot.goals[1:]))
    )


def test_update_target_event_replaces_only_the_matching_event(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    updated = replace(
        snapshot.target_events[0],
        name="Updated event",
        event_date=date(2001, 1, 1),
        event_type=TargetEventType.OTHER,
        status=TargetEventStatus.CANCELLED,
    )

    use_cases.update_target_event(updated)

    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        replace(snapshot, target_events=(updated, snapshot.target_events[1]))
    )


def test_multiple_goals_can_be_created_for_the_same_event(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    first = use_cases.create_goal(
        title="First goal",
        status=GoalStatus.ACTIVE,
        target_event_id=snapshot.target_events[0].id,
    )
    store.load.return_value = store.save.call_args.args[0]

    second = use_cases.create_goal(
        title="Second goal",
        status=GoalStatus.ACTIVE,
        target_event_id=snapshot.target_events[0].id,
    )

    assert first.id != second.id
    assert first.target_event_id == second.target_event_id
    assert store.save.call_args.args[0] == replace(
        snapshot, goals=(*snapshot.goals, first, second)
    )


def test_create_goal_rejects_a_missing_event_reference_without_saving(
    store: Mock,
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    missing_id = UUID(int=99)

    with pytest.raises(LookupError, match=f"Target event {missing_id} does not exist"):
        use_cases.create_goal(
            title="Goal",
            status=GoalStatus.ACTIVE,
            target_event_id=missing_id,
        )

    store.save.assert_not_called()


def test_update_goal_rejects_a_missing_event_reference_without_saving(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    missing_id = UUID(int=99)
    updated = replace(snapshot.goals[0], target_event_id=missing_id)

    with pytest.raises(LookupError, match=f"Target event {missing_id} does not exist"):
        use_cases.update_goal(updated)

    store.save.assert_not_called()


def test_delete_goal_leaves_its_event_and_other_goals_untouched(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    use_cases.delete_goal(snapshot.goals[0].id)

    store.load.assert_called_once_with()
    store.save.assert_called_once_with(replace(snapshot, goals=snapshot.goals[1:]))


def test_delete_event_unlinks_all_its_goals_in_one_snapshot_save(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    use_cases.delete_target_event(snapshot.target_events[0].id)

    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        GoalsAndEventsSnapshot(
            goals=(
                replace(snapshot.goals[0], target_event_id=None),
                replace(snapshot.goals[1], target_event_id=None),
                snapshot.goals[2],
            ),
            target_events=(snapshot.target_events[1],),
        )
    )
    assert snapshot.goals[0].target_event_id == snapshot.target_events[0].id
    assert snapshot.goals[1].target_event_id == snapshot.target_events[0].id


def test_delete_event_without_linked_goals_leaves_all_goals_untouched(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)

    use_cases.delete_target_event(snapshot.target_events[1].id)

    store.save.assert_called_once_with(
        replace(snapshot, target_events=(snapshot.target_events[0],))
    )


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_missing_goal_is_reported_explicitly_without_saving(
    store: Mock, snapshot: GoalsAndEventsSnapshot, operation: str
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    missing_id = UUID(int=99)

    with pytest.raises(LookupError, match=f"Goal {missing_id} does not exist"):
        if operation == "get":
            use_cases.get_goal(missing_id)
        elif operation == "update":
            use_cases.update_goal(replace(snapshot.goals[0], id=missing_id))
        else:
            use_cases.delete_goal(missing_id)

    store.save.assert_not_called()


@pytest.mark.parametrize("operation", ["get", "update", "delete"])
def test_missing_target_event_is_reported_explicitly_without_saving(
    store: Mock, snapshot: GoalsAndEventsSnapshot, operation: str
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    missing_id = UUID(int=99)

    with pytest.raises(LookupError, match=f"Target event {missing_id} does not exist"):
        if operation == "get":
            use_cases.get_target_event(missing_id)
        elif operation == "update":
            use_cases.update_target_event(
                replace(snapshot.target_events[0], id=missing_id)
            )
        else:
            use_cases.delete_target_event(missing_id)

    store.save.assert_not_called()


def test_cancelling_event_cancels_only_active_linked_goals_in_one_save(
    store: Mock, cancellation_snapshot: GoalsAndEventsSnapshot
) -> None:
    store.load.return_value = cancellation_snapshot
    use_cases = GoalsAndEventsUseCases(store)
    cancelled_event = replace(
        cancellation_snapshot.target_events[0], status=TargetEventStatus.CANCELLED
    )

    use_cases.update_target_event(cancelled_event)

    store.load.assert_called_once_with()
    store.save.assert_called_once_with(
        replace(
            cancellation_snapshot,
            goals=(
                replace(cancellation_snapshot.goals[0], status=GoalStatus.CANCELLED),
                replace(cancellation_snapshot.goals[1], status=GoalStatus.CANCELLED),
                *cancellation_snapshot.goals[2:],
            ),
            target_events=(cancelled_event, cancellation_snapshot.target_events[1]),
        )
    )
    saved = store.save.call_args.args[0]
    assert all(
        actual is original
        for actual, original in zip(
            saved.goals[2:], cancellation_snapshot.goals[2:], strict=True
        )
    )
    assert cancellation_snapshot.goals[0].status is GoalStatus.ACTIVE
    assert cancellation_snapshot.goals[1].status is GoalStatus.ACTIVE


def test_cancelling_goal_leaves_its_event_and_other_linked_goals_unchanged(
    store: Mock, cancellation_snapshot: GoalsAndEventsSnapshot
) -> None:
    store.load.return_value = cancellation_snapshot
    use_cases = GoalsAndEventsUseCases(store)
    cancelled_goal = replace(
        cancellation_snapshot.goals[0],
        status=GoalStatus.CANCELLED,
    )

    use_cases.update_goal(cancelled_goal)

    store.save.assert_called_once_with(
        replace(
            cancellation_snapshot,
            goals=(cancelled_goal, *cancellation_snapshot.goals[1:]),
        )
    )


def test_reactivating_event_does_not_reactivate_cancelled_goals(
    store: Mock, cancellation_snapshot: GoalsAndEventsSnapshot
) -> None:
    store.load.return_value = cancellation_snapshot
    use_cases = GoalsAndEventsUseCases(store)
    cancelled_event = replace(
        cancellation_snapshot.target_events[0], status=TargetEventStatus.CANCELLED
    )
    use_cases.update_target_event(cancelled_event)
    cancelled_snapshot = store.save.call_args.args[0]
    store.load.return_value = cancelled_snapshot
    store.save.reset_mock()
    reactivated_event = replace(cancelled_event, status=TargetEventStatus.ACTIVE)

    use_cases.update_target_event(reactivated_event)

    store.save.assert_called_once_with(
        replace(
            cancelled_snapshot,
            target_events=(reactivated_event, cancelled_snapshot.target_events[1]),
        )
    )
    assert store.save.call_args.args[0].goals[0].status is GoalStatus.CANCELLED
    assert store.save.call_args.args[0].goals[1].status is GoalStatus.CANCELLED


@pytest.mark.parametrize(
    "event_status", [TargetEventStatus.COMPLETED, TargetEventStatus.INACTIVE]
)
def test_completing_or_deactivating_event_does_not_cancel_linked_goals(
    store: Mock,
    cancellation_snapshot: GoalsAndEventsSnapshot,
    event_status: TargetEventStatus,
) -> None:
    store.load.return_value = cancellation_snapshot
    use_cases = GoalsAndEventsUseCases(store)
    updated_event = replace(
        cancellation_snapshot.target_events[0],
        status=event_status,
    )

    use_cases.update_target_event(updated_event)

    store.save.assert_called_once_with(
        replace(
            cancellation_snapshot,
            target_events=(updated_event, cancellation_snapshot.target_events[1]),
        )
    )


@pytest.mark.parametrize("operation", ["create", "update"])
def test_active_goal_cannot_reference_a_cancelled_event(
    store: Mock, snapshot: GoalsAndEventsSnapshot, operation: str
) -> None:
    cancelled_event = replace(
        snapshot.target_events[0], status=TargetEventStatus.CANCELLED
    )
    store.load.return_value = replace(
        snapshot, target_events=(cancelled_event, snapshot.target_events[1])
    )
    use_cases = GoalsAndEventsUseCases(store)

    with pytest.raises(ValueError, match="active goal.*cancelled target event"):
        if operation == "create":
            use_cases.create_goal(
                title="New active goal",
                status=GoalStatus.ACTIVE,
                target_event_id=cancelled_event.id,
            )
        else:
            use_cases.update_goal(replace(snapshot.goals[0], status=GoalStatus.ACTIVE))

    store.save.assert_not_called()


@pytest.mark.parametrize("operation", ["create", "update"])
@pytest.mark.parametrize(
    "goal_status", [GoalStatus.COMPLETED, GoalStatus.INACTIVE, GoalStatus.CANCELLED]
)
def test_non_active_goal_can_reference_a_cancelled_event(
    store: Mock,
    snapshot: GoalsAndEventsSnapshot,
    operation: str,
    goal_status: GoalStatus,
) -> None:
    cancelled_event = replace(
        snapshot.target_events[0], status=TargetEventStatus.CANCELLED
    )
    store.load.return_value = replace(
        snapshot, target_events=(cancelled_event, snapshot.target_events[1])
    )
    use_cases = GoalsAndEventsUseCases(store)

    if operation == "create":
        use_cases.create_goal(
            title="Historical goal",
            status=goal_status,
            target_event_id=cancelled_event.id,
        )
        saved_goal = store.save.call_args.args[0].goals[-1]
    else:
        use_cases.update_goal(replace(snapshot.goals[0], status=goal_status))
        saved_goal = store.save.call_args.args[0].goals[0]

    assert saved_goal.status is goal_status
    assert saved_goal.target_event_id == cancelled_event.id
    store.save.assert_called_once()


def test_cancelled_goal_can_be_explicitly_activated_for_an_active_event(
    store: Mock, snapshot: GoalsAndEventsSnapshot
) -> None:
    use_cases = GoalsAndEventsUseCases(store)
    activated_goal = replace(snapshot.goals[1], status=GoalStatus.ACTIVE)

    use_cases.update_goal(activated_goal)

    store.save.assert_called_once_with(
        replace(snapshot, goals=(snapshot.goals[0], activated_goal, snapshot.goals[2]))
    )


def test_deleting_event_unlinks_goals_without_changing_any_goal_status(
    store: Mock, cancellation_snapshot: GoalsAndEventsSnapshot
) -> None:
    store.load.return_value = cancellation_snapshot
    use_cases = GoalsAndEventsUseCases(store)
    event_id = cancellation_snapshot.target_events[0].id

    use_cases.delete_target_event(event_id)

    store.save.assert_called_once_with(
        replace(
            cancellation_snapshot,
            goals=tuple(
                replace(goal, target_event_id=None)
                for goal in cancellation_snapshot.goals[:5]
            )
            + cancellation_snapshot.goals[5:],
            target_events=(cancellation_snapshot.target_events[1],),
        )
    )
