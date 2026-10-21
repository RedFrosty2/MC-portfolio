from dataclasses import FrozenInstanceError, replace
from datetime import date
from uuid import UUID

import pytest

from odysseus.domain.goals import Goal, GoalStatus
from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)
from odysseus.web.presentation.goals_and_events import (
    GoalRowView,
    GoalsAndEventsView,
    TargetEventRowView,
    build_goals_and_events_view,
)


@pytest.fixture
def goal() -> Goal:
    return Goal(id=UUID(int=1), title="Bench press 120 kg", status=GoalStatus.ACTIVE)


@pytest.fixture
def event() -> TargetEvent:
    return TargetEvent(
        id=UUID(int=2),
        name="Manchester Half Marathon",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )


def test_standalone_strength_goal_has_no_deadline_or_linked_event(goal: Goal) -> None:
    view = build_goals_and_events_view(goals=(goal,), target_events=())

    assert view.goals == (
        GoalRowView(
            id=goal.id,
            title="Bench press 120 kg",
            status_label="Active",
            target_date_label="No deadline",
            linked_event_label=None,
        ),
    )
    assert view.target_events == ()


def test_goal_and_event_dates_use_the_same_readable_format(
    goal: Goal, event: TargetEvent
) -> None:
    goal = replace(goal, target_date=date(2030, 1, 9))
    event = replace(event, event_date=date(2030, 1, 9))

    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    assert view.goals[0].target_date_label == "09 Jan 2030"
    assert view.target_events[0].event_date_label == "09 Jan 2030"


def test_multiple_goals_resolve_the_name_of_the_same_linked_event(
    goal: Goal, event: TargetEvent
) -> None:
    first = replace(goal, title="Finish the half marathon", target_event_id=event.id)
    second = replace(first, id=UUID(int=3), title="Run under two hours")

    view = build_goals_and_events_view(goals=(first, second), target_events=(event,))

    assert tuple(row.linked_event_label for row in view.goals) == (
        "Manchester Half Marathon",
        "Manchester Half Marathon",
    )
    assert tuple(row.id for row in view.goals) == (first.id, second.id)


def test_event_without_linked_goals_is_still_displayed(event: TargetEvent) -> None:
    view = build_goals_and_events_view(goals=(), target_events=(event,))

    assert view.goals == ()
    assert view.target_events == (
        TargetEventRowView(
            id=event.id,
            name="Manchester Half Marathon",
            event_type_label="Running",
            event_date_label="01 May 2030",
            status_label="Active",
        ),
    )


@pytest.mark.parametrize(
    "status, label",
    [
        (GoalStatus.ACTIVE, "Active"),
        (GoalStatus.COMPLETED, "Completed"),
        (GoalStatus.CANCELLED, "Cancelled"),
        (GoalStatus.INACTIVE, "Inactive"),
    ],
)
def test_goal_status_labels_are_readable(
    goal: Goal, status: GoalStatus, label: str
) -> None:
    goal = replace(goal, status=status)

    view = build_goals_and_events_view(goals=(goal,), target_events=())

    assert view.goals[0].status_label == label


@pytest.mark.parametrize(
    "status, label",
    [
        (TargetEventStatus.ACTIVE, "Active"),
        (TargetEventStatus.COMPLETED, "Completed"),
        (TargetEventStatus.CANCELLED, "Cancelled"),
        (TargetEventStatus.INACTIVE, "Inactive"),
    ],
)
def test_event_status_labels_are_readable(
    event: TargetEvent, status: TargetEventStatus, label: str
) -> None:
    event = replace(event, status=status)

    view = build_goals_and_events_view(goals=(), target_events=(event,))

    assert view.target_events[0].status_label == label


@pytest.mark.parametrize(
    "event_type, label",
    [
        (TargetEventType.RUNNING, "Running"),
        (TargetEventType.HYROX, "HYROX"),
        (TargetEventType.STRENGTH, "Strength"),
        (TargetEventType.OTHER, "Other"),
    ],
)
def test_event_type_labels_are_readable(
    event: TargetEvent, event_type: TargetEventType, label: str
) -> None:
    event = replace(event, event_type=event_type)

    view = build_goals_and_events_view(goals=(), target_events=(event,))

    assert view.target_events[0].event_type_label == label


@pytest.mark.parametrize(
    "goal_status, event_status, label",
    [
        (GoalStatus.ACTIVE, TargetEventStatus.ACTIVE, "Active"),
        (GoalStatus.COMPLETED, TargetEventStatus.COMPLETED, "Completed"),
        (GoalStatus.CANCELLED, TargetEventStatus.CANCELLED, "Cancelled"),
        (GoalStatus.INACTIVE, TargetEventStatus.INACTIVE, "Inactive"),
    ],
)
def test_historical_entries_keep_their_labels_and_event_links(
    goal: Goal,
    event: TargetEvent,
    goal_status: GoalStatus,
    event_status: TargetEventStatus,
    label: str,
) -> None:
    event = replace(event, event_date=date(2000, 5, 1), status=event_status)
    goal = replace(
        goal,
        status=goal_status,
        target_date=date(2000, 4, 1),
        target_event_id=event.id,
    )

    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    assert view.goals[0].target_date_label == "01 Apr 2000"
    assert view.goals[0].linked_event_label == event.name
    assert view.goals[0].status_label == label
    assert view.target_events[0].event_date_label == "01 May 2000"
    assert view.target_events[0].status_label == label


def test_empty_inputs_produce_empty_view_tuples() -> None:
    view = build_goals_and_events_view(goals=(), target_events=())

    assert view == GoalsAndEventsView(goals=(), target_events=())


def test_goal_and_event_order_matches_the_supplied_order(
    goal: Goal, event: TargetEvent
) -> None:
    later_event = replace(event, id=UUID(int=20), event_date=date(2031, 1, 1))
    earlier_event = replace(event, id=UUID(int=10), event_date=date(2000, 1, 1))
    later_goal = replace(goal, id=UUID(int=20), target_date=date(2031, 1, 1))
    earlier_goal = replace(goal, id=UUID(int=10), target_date=date(2000, 1, 1))

    view = build_goals_and_events_view(
        goals=(later_goal, goal, earlier_goal),
        target_events=(later_event, event, earlier_event),
    )

    assert tuple(row.id for row in view.goals) == (
        later_goal.id,
        goal.id,
        earlier_goal.id,
    )
    assert tuple(row.id for row in view.target_events) == (
        later_event.id,
        event.id,
        earlier_event.id,
    )


def test_missing_event_reference_is_distinct_from_a_standalone_goal(goal: Goal) -> None:
    linked_goal = replace(goal, id=UUID(int=3), target_event_id=UUID(int=99))

    view = build_goals_and_events_view(goals=(goal, linked_goal), target_events=())

    assert view.goals[0].linked_event_label is None
    assert view.goals[1].linked_event_label == "Unresolved event reference"


def test_building_a_view_does_not_mutate_supplied_domain_objects(
    goal: Goal, event: TargetEvent
) -> None:
    goals = (replace(goal, target_event_id=event.id),)
    events = (event,)
    original_goal = replace(goals[0])
    original_event = replace(event)

    build_goals_and_events_view(goals=goals, target_events=events)

    assert goals == (original_goal,)
    assert events == (original_event,)
    assert events[0] is event


def test_cancelled_event_does_not_change_the_supplied_goal_status(
    goal: Goal, event: TargetEvent
) -> None:
    event = replace(event, status=TargetEventStatus.CANCELLED)
    goal = replace(goal, target_event_id=event.id)

    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    assert view.goals[0].status_label == "Active"
    assert view.goals[0].linked_event_label == event.name
    assert view.target_events[0].status_label == "Cancelled"
    assert goal.status is GoalStatus.ACTIVE


def test_presentation_rows_and_collections_are_immutable(
    goal: Goal, event: TargetEvent
) -> None:
    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    with pytest.raises(FrozenInstanceError):
        view.goals[0].title = "Changed"
    with pytest.raises(FrozenInstanceError):
        view.target_events[0].name = "Changed"
    with pytest.raises(FrozenInstanceError):
        view.goals = ()
    with pytest.raises(FrozenInstanceError):
        view.target_events = ()


@pytest.mark.parametrize("target_event_id", [UUID(int=2), UUID(int=99)])
def test_own_target_date_takes_precedence_over_linked_event_context(
    goal: Goal, event: TargetEvent, target_event_id: UUID
) -> None:
    goal = replace(
        goal,
        target_date=date(2030, 1, 9),
        target_event_id=target_event_id,
    )

    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    assert view.goals[0].target_date_label == "09 Jan 2030"


def test_undated_linked_goal_displays_its_event_date(
    goal: Goal, event: TargetEvent
) -> None:
    goal = replace(goal, target_event_id=event.id)

    view = build_goals_and_events_view(goals=(goal,), target_events=(event,))

    assert view.goals[0].target_date_label == "Event date: 01 May 2030"
    assert view.goals[0].linked_event_label == event.name


def test_missing_event_date_is_unavailable_for_an_undated_goal(goal: Goal) -> None:
    goal = replace(goal, target_event_id=UUID(int=99))

    view = build_goals_and_events_view(goals=(goal,), target_events=())

    assert view.goals[0].target_date_label == "Event date unavailable"
    assert view.goals[0].linked_event_label == "Unresolved event reference"
