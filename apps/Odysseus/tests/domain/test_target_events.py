from dataclasses import FrozenInstanceError
from datetime import date
from uuid import UUID

import pytest

from odysseus.domain.target_events import (
    TargetEvent,
    TargetEventStatus,
    TargetEventType,
)


def test_target_event_can_exist_without_linked_goals() -> None:
    event_id = UUID(int=2)
    event_date = date(2030, 5, 1)

    event = TargetEvent(
        id=event_id,
        name="Local half marathon",
        event_date=event_date,
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )

    assert event.id == event_id
    assert event.name == "Local half marathon"
    assert event.event_date == event_date
    assert event.event_type is TargetEventType.RUNNING
    assert event.status is TargetEventStatus.ACTIVE


@pytest.mark.parametrize(
    "event_type, string_value",
    [
        (TargetEventType.RUNNING, "running"),
        (TargetEventType.HYROX, "hyrox"),
        (TargetEventType.STRENGTH, "strength"),
        (TargetEventType.OTHER, "other"),
    ],
)
def test_target_event_supports_each_explicit_event_type(
    event_type: TargetEventType, string_value: str
) -> None:
    event = TargetEvent(
        id=UUID(int=2),
        name="Target event",
        event_date=date(2030, 5, 1),
        event_type=event_type,
        status=TargetEventStatus.ACTIVE,
    )

    assert event.event_type is event_type
    assert str(event.event_type) == string_value


@pytest.mark.parametrize(
    "status, string_value",
    [
        (TargetEventStatus.ACTIVE, "active"),
        (TargetEventStatus.COMPLETED, "completed"),
        (TargetEventStatus.CANCELLED, "cancelled"),
        (TargetEventStatus.INACTIVE, "inactive"),
    ],
)
def test_target_event_supports_each_explicit_status(
    status: TargetEventStatus, string_value: str
) -> None:
    event = TargetEvent(
        id=UUID(int=2),
        name="Target event",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.OTHER,
        status=status,
    )

    assert event.status is status
    assert str(event.status) == string_value


@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_target_event_rejects_an_empty_or_whitespace_only_name(name: str) -> None:
    with pytest.raises(ValueError, match="target event name"):
        TargetEvent(
            id=UUID(int=2),
            name=name,
            event_date=date(2030, 5, 1),
            event_type=TargetEventType.OTHER,
            status=TargetEventStatus.ACTIVE,
        )


def test_target_event_accepts_a_past_date_without_changing_status() -> None:
    past_date = date(2000, 5, 1)

    event = TargetEvent(
        id=UUID(int=2),
        name="Historical race",
        event_date=past_date,
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )

    assert event.event_date == past_date
    assert event.status is TargetEventStatus.ACTIVE


def test_target_event_is_immutable() -> None:
    event = TargetEvent(
        id=UUID(int=2),
        name="Target event",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.OTHER,
        status=TargetEventStatus.ACTIVE,
    )

    with pytest.raises(FrozenInstanceError):
        event.name = "A different event"
