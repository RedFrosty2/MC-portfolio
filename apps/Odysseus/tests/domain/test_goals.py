from dataclasses import FrozenInstanceError
from datetime import date
from uuid import UUID

import pytest

from odysseus.domain.goals import Goal, GoalStatus


def test_goal_can_exist_without_a_target_date_or_event() -> None:
    goal_id = UUID(int=1)

    goal = Goal(id=goal_id, title="Improve running endurance", status=GoalStatus.ACTIVE)

    assert goal.id == goal_id
    assert goal.title == "Improve running endurance"
    assert goal.status is GoalStatus.ACTIVE
    assert goal.target_date is None
    assert goal.target_event_id is None


@pytest.mark.parametrize("target_date", [date(2000, 5, 1), date(2030, 5, 1)])
def test_goal_accepts_a_past_or_future_target_date_without_changing_status(
    target_date: date,
) -> None:
    goal = Goal(
        id=UUID(int=1),
        title="Run a half marathon",
        status=GoalStatus.ACTIVE,
        target_date=target_date,
    )

    assert goal.target_date == target_date
    assert goal.status is GoalStatus.ACTIVE
    assert goal.target_event_id is None


def test_goal_can_reference_a_target_event_without_a_target_date() -> None:
    event_id = UUID(int=2)

    goal = Goal(
        id=UUID(int=1),
        title="Finish a HYROX race",
        status=GoalStatus.ACTIVE,
        target_event_id=event_id,
    )

    assert goal.target_event_id == event_id
    assert goal.target_date is None


@pytest.mark.parametrize(
    "status, string_value",
    [
        (GoalStatus.ACTIVE, "active"),
        (GoalStatus.COMPLETED, "completed"),
        (GoalStatus.CANCELLED, "cancelled"),
        (GoalStatus.INACTIVE, "inactive"),
    ],
)
def test_goal_supports_each_explicit_status(
    status: GoalStatus, string_value: str
) -> None:
    goal = Goal(id=UUID(int=1), title="Improve endurance", status=status)

    assert goal.status is status
    assert str(goal.status) == string_value


@pytest.mark.parametrize("title", ["", "   ", "\t\n"])
def test_goal_rejects_an_empty_or_whitespace_only_title(title: str) -> None:
    with pytest.raises(ValueError, match="goal title"):
        Goal(id=UUID(int=1), title=title, status=GoalStatus.ACTIVE)


def test_goal_is_immutable() -> None:
    goal = Goal(id=UUID(int=1), title="Improve endurance", status=GoalStatus.ACTIVE)

    with pytest.raises(FrozenInstanceError):
        goal.title = "A different goal"
