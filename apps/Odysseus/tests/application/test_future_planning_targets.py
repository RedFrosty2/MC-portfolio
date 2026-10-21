from dataclasses import FrozenInstanceError, replace
from datetime import date
from unittest.mock import Mock
from uuid import UUID

import pytest

from odysseus.application.contracts import GoalsAndEventsSnapshot, GoalsAndEventsStore
from odysseus.application.goals_and_events import (
    FuturePlanningTargets,
    GoalsAndEventsUseCases,
)
from odysseus.domain.goals import Goal, GoalStatus
from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)


@pytest.fixture
def as_of() -> date:
    return date(2030, 5, 1)


@pytest.fixture
def goal() -> Goal:
    return Goal(id=UUID(int=1), title="Improve endurance", status=GoalStatus.ACTIVE)


@pytest.fixture
def event() -> TargetEvent:
    return TargetEvent(
        id=UUID(int=2),
        name="Half marathon",
        event_date=date(2030, 6, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )


@pytest.fixture
def store() -> Mock:
    store = Mock(spec=GoalsAndEventsStore)
    store.load.return_value = GoalsAndEventsSnapshot()
    return store


@pytest.mark.parametrize(
    "target_date, included",
    [
        (None, True),
        (date(2030, 6, 1), True),
        (date(2030, 5, 1), True),
        (date(2030, 4, 30), False),
    ],
)
def test_active_standalone_goal_uses_an_inclusive_optional_date_cutoff(
    store: Mock, goal: Goal, as_of: date, target_date: date | None, included: bool
) -> None:
    goal = replace(goal, target_date=target_date)
    store.load.return_value = GoalsAndEventsSnapshot(goals=(goal,))

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.goals == ((goal,) if included else ())


@pytest.mark.parametrize(
    "status", [GoalStatus.COMPLETED, GoalStatus.CANCELLED, GoalStatus.INACTIVE]
)
def test_non_active_standalone_and_linked_goals_are_excluded(
    store: Mock, goal: Goal, event: TargetEvent, as_of: date, status: GoalStatus
) -> None:
    standalone = replace(goal, status=status)
    linked = replace(standalone, id=UUID(int=3), target_event_id=event.id)
    store.load.return_value = GoalsAndEventsSnapshot(
        goals=(standalone, linked), target_events=(event,)
    )

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.goals == ()
    assert result.target_events == (event,)


@pytest.mark.parametrize(
    "event_date, included",
    [
        (date(2030, 6, 1), True),
        (date(2030, 5, 1), True),
        (date(2030, 4, 30), False),
    ],
)
def test_active_event_uses_an_inclusive_date_cutoff(
    store: Mock, event: TargetEvent, as_of: date, event_date: date, included: bool
) -> None:
    event = replace(event, event_date=event_date)
    store.load.return_value = GoalsAndEventsSnapshot(target_events=(event,))

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.target_events == ((event,) if included else ())


@pytest.mark.parametrize(
    "status",
    [
        TargetEventStatus.COMPLETED,
        TargetEventStatus.CANCELLED,
        TargetEventStatus.INACTIVE,
    ],
)
def test_non_active_event_is_excluded(
    store: Mock, event: TargetEvent, as_of: date, status: TargetEventStatus
) -> None:
    event = replace(event, status=status)
    store.load.return_value = GoalsAndEventsSnapshot(target_events=(event,))

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.target_events == ()


@pytest.mark.parametrize(
    "target_date, included",
    [
        (None, True),
        (date(2030, 6, 1), True),
        (date(2030, 5, 1), True),
        (date(2030, 4, 30), False),
    ],
)
def test_linked_goal_must_also_satisfy_its_own_target_date(
    store: Mock,
    goal: Goal,
    event: TargetEvent,
    as_of: date,
    target_date: date | None,
    included: bool,
) -> None:
    goal = replace(goal, target_date=target_date, target_event_id=event.id)
    store.load.return_value = GoalsAndEventsSnapshot(
        goals=(goal,), target_events=(event,)
    )

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.goals == ((goal,) if included else ())
    assert result.target_events == (event,)


@pytest.mark.parametrize(
    "event_date, event_status",
    [
        (date(2030, 4, 30), TargetEventStatus.ACTIVE),
        (date(2030, 6, 1), TargetEventStatus.COMPLETED),
        (date(2030, 6, 1), TargetEventStatus.CANCELLED),
        (date(2030, 6, 1), TargetEventStatus.INACTIVE),
    ],
)
def test_linked_goal_is_excluded_when_its_event_is_past_or_non_active(
    store: Mock,
    goal: Goal,
    event: TargetEvent,
    as_of: date,
    event_date: date,
    event_status: TargetEventStatus,
) -> None:
    event = replace(event, event_date=event_date, status=event_status)
    goal = replace(goal, target_event_id=event.id)
    store.load.return_value = GoalsAndEventsSnapshot(
        goals=(goal,), target_events=(event,)
    )

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.goals == ()
    assert result.target_events == ()


def test_linked_goal_is_excluded_when_its_event_is_missing(
    store: Mock, goal: Goal, as_of: date
) -> None:
    goal = replace(goal, target_event_id=UUID(int=99))
    store.load.return_value = GoalsAndEventsSnapshot(goals=(goal,))

    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result.goals == ()


def test_query_preserves_order_identity_and_history_with_one_read_and_no_save(
    store: Mock, goal: Goal, event: TargetEvent, as_of: date
) -> None:
    later_event = replace(event, id=UUID(int=20), event_date=date(2031, 1, 1))
    same_day_event = replace(event, id=UUID(int=10), event_date=as_of)
    past_event = replace(event, id=UUID(int=30), event_date=date(2000, 1, 1))
    completed_event = replace(
        event, id=UUID(int=40), status=TargetEventStatus.COMPLETED
    )
    later_goal = replace(
        goal,
        id=UUID(int=20),
        target_date=date(2031, 1, 1),
        target_event_id=later_event.id,
    )
    past_goal = replace(goal, id=UUID(int=30), target_date=date(2000, 1, 1))
    completed_goal = replace(goal, id=UUID(int=40), status=GoalStatus.COMPLETED)
    same_day_goal = replace(
        goal, id=UUID(int=10), target_date=as_of, target_event_id=same_day_event.id
    )
    snapshot = GoalsAndEventsSnapshot(
        goals=(later_goal, past_goal, goal, completed_goal, same_day_goal),
        target_events=(later_event, past_event, completed_event, same_day_event),
    )
    store.load.return_value = snapshot
    use_cases = GoalsAndEventsUseCases(store)

    result = use_cases.get_future_planning_targets(as_of)

    store.load.assert_called_once_with()
    store.save.assert_not_called()
    assert result == FuturePlanningTargets(
        goals=(later_goal, goal, same_day_goal),
        target_events=(later_event, same_day_event),
    )
    assert all(
        actual is original
        for actual, original in zip(
            result.goals, (later_goal, goal, same_day_goal), strict=True
        )
    )
    assert result.target_events[0] is later_event
    assert result.target_events[1] is same_day_event
    assert use_cases.list_goals() is snapshot.goals
    assert use_cases.list_target_events() is snapshot.target_events
    assert use_cases.get_goal(past_goal.id) is past_goal
    assert use_cases.get_goal(completed_goal.id) is completed_goal
    assert use_cases.get_target_event(past_event.id) is past_event
    assert use_cases.get_target_event(completed_event.id) is completed_event
    assert past_goal.status is GoalStatus.ACTIVE
    assert past_event.status is TargetEventStatus.ACTIVE
    assert completed_goal.status is GoalStatus.COMPLETED
    assert completed_event.status is TargetEventStatus.COMPLETED
    store.save.assert_not_called()


def test_empty_snapshot_produces_empty_future_planning_targets(
    store: Mock, as_of: date
) -> None:
    result = GoalsAndEventsUseCases(store).get_future_planning_targets(as_of)

    assert result == FuturePlanningTargets(goals=(), target_events=())


def test_future_planning_targets_are_immutable() -> None:
    result = FuturePlanningTargets(goals=(), target_events=())

    with pytest.raises(FrozenInstanceError):
        result.goals = ()
