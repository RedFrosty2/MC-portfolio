from dataclasses import FrozenInstanceError
from datetime import date
from urllib.parse import urlencode
from uuid import UUID

import pytest

from odysseus.domain.goals import GoalStatus
from odysseus.domain.target_events import TargetEventStatus, TargetEventType
from odysseus.web.forms import (
    GoalFormValues,
    TargetEventFormValues,
    parse_goal_form,
    parse_target_event_form,
)

INVALID_DATES = (
    "2030-02-30",
    "2030-2-03",
    "20300203",
    "2030-W05-1",
    "03/02/2030",
    "2030-02-03T00:00:00",
    " 2030-05-01 ",
    "not-a-date",
)


@pytest.fixture
def goal_fields() -> dict[str, str]:
    return {"title": "  Bench press 120 kg  ", "status": "active"}


@pytest.fixture
def event_fields() -> dict[str, str]:
    return {
        "name": "  Manchester Half Marathon  ",
        "event_date": "2030-05-01",
        "event_type": "running",
        "status": "active",
    }


def test_goal_form_parses_a_standalone_goal(goal_fields: dict[str, str]) -> None:
    values = parse_goal_form(urlencode(goal_fields))

    assert values == GoalFormValues(
        title="Bench press 120 kg",
        status=GoalStatus.ACTIVE,
        target_date=None,
        target_event_id=None,
    )


def test_goal_form_parses_an_event_reference_without_resolving_it(
    goal_fields: dict[str, str],
) -> None:
    event_id = UUID(int=99)
    goal_fields["target_event_id"] = str(event_id)

    values = parse_goal_form(urlencode(goal_fields))

    assert isinstance(values.target_event_id, UUID)
    assert values.target_event_id == event_id


@pytest.mark.parametrize(
    "optional_fields",
    [
        {},
        {"target_date": "", "target_event_id": ""},
        {"target_date": " \t ", "target_event_id": " \t "},
    ],
)
def test_goal_form_treats_omitted_or_blank_optional_fields_as_none(
    goal_fields: dict[str, str], optional_fields: dict[str, str]
) -> None:
    values = parse_goal_form(urlencode(goal_fields | optional_fields))

    assert values.target_date is None
    assert values.target_event_id is None


@pytest.mark.parametrize("target_date", [date(2030, 5, 1), date(2000, 1, 1)])
def test_goal_form_accepts_html_dates_including_historical_dates(
    goal_fields: dict[str, str], target_date: date
) -> None:
    goal_fields["target_date"] = target_date.isoformat()

    values = parse_goal_form(urlencode(goal_fields))

    assert values.target_date == target_date


@pytest.mark.parametrize("value", INVALID_DATES)
def test_goal_form_rejects_invalid_or_non_html_dates(
    goal_fields: dict[str, str], value: str
) -> None:
    goal_fields["target_date"] = value

    with pytest.raises(ValueError, match="target_date.*YYYY-MM-DD"):
        parse_goal_form(urlencode(goal_fields))


@pytest.mark.parametrize("value", ["not-a-uuid", "1234"])
def test_goal_form_rejects_malformed_event_uuids(
    goal_fields: dict[str, str], value: str
) -> None:
    goal_fields["target_event_id"] = value

    with pytest.raises(ValueError, match="target_event_id.*UUID"):
        parse_goal_form(urlencode(goal_fields))


@pytest.mark.parametrize("status", list(GoalStatus))
def test_goal_form_parses_each_explicit_status(
    goal_fields: dict[str, str], status: GoalStatus
) -> None:
    goal_fields["status"] = status.value

    values = parse_goal_form(urlencode(goal_fields))

    assert values.status is status


@pytest.mark.parametrize("value", ["", "ACTIVE", "unknown"])
def test_goal_form_rejects_invalid_status_instead_of_defaulting(
    goal_fields: dict[str, str], value: str
) -> None:
    goal_fields["status"] = value

    with pytest.raises(ValueError, match="Invalid status"):
        parse_goal_form(urlencode(goal_fields))


@pytest.mark.parametrize("field", ["title", "status"])
def test_goal_form_reports_missing_required_fields(
    goal_fields: dict[str, str], field: str
) -> None:
    del goal_fields[field]

    with pytest.raises(ValueError, match=f"Missing required field: {field}"):
        parse_goal_form(urlencode(goal_fields))


@pytest.mark.parametrize("title", ["", " \t\n "])
def test_goal_form_leaves_blank_title_validation_to_the_domain(
    goal_fields: dict[str, str], title: str
) -> None:
    goal_fields["title"] = title

    values = parse_goal_form(urlencode(goal_fields))

    assert values.title == ""


def test_goal_form_decodes_special_characters_and_trims_only_surrounding_text(
    goal_fields: dict[str, str],
) -> None:
    goal_fields["title"] = "  Strength & endurance + 10% / café  "

    values = parse_goal_form(urlencode(goal_fields))

    assert values.title == "Strength & endurance + 10% / café"


def test_event_form_parses_a_running_event(event_fields: dict[str, str]) -> None:
    values = parse_target_event_form(urlencode(event_fields))

    assert values == TargetEventFormValues(
        name="Manchester Half Marathon",
        event_date=date(2030, 5, 1),
        event_type=TargetEventType.RUNNING,
        status=TargetEventStatus.ACTIVE,
    )


@pytest.mark.parametrize("event_type", list(TargetEventType))
def test_event_form_parses_running_hyrox_strength_and_other_types(
    event_fields: dict[str, str], event_type: TargetEventType
) -> None:
    event_fields["event_type"] = event_type.value

    values = parse_target_event_form(urlencode(event_fields))

    assert values.event_type is event_type


@pytest.mark.parametrize("status", list(TargetEventStatus))
def test_event_form_parses_each_explicit_status(
    event_fields: dict[str, str], status: TargetEventStatus
) -> None:
    event_fields["status"] = status.value

    values = parse_target_event_form(urlencode(event_fields))

    assert values.status is status


def test_event_form_accepts_a_past_date_without_changing_status(
    event_fields: dict[str, str],
) -> None:
    event_fields["event_date"] = "2000-05-01"

    values = parse_target_event_form(urlencode(event_fields))

    assert values.event_date == date(2000, 5, 1)
    assert values.status is TargetEventStatus.ACTIVE


@pytest.mark.parametrize("value", ["", " ", *INVALID_DATES])
def test_event_form_rejects_blank_invalid_or_non_html_dates(
    event_fields: dict[str, str], value: str
) -> None:
    event_fields["event_date"] = value

    with pytest.raises(ValueError, match="event_date.*YYYY-MM-DD"):
        parse_target_event_form(urlencode(event_fields))


@pytest.mark.parametrize("field", ["name", "event_date", "event_type", "status"])
def test_event_form_reports_missing_required_fields(
    event_fields: dict[str, str], field: str
) -> None:
    del event_fields[field]

    with pytest.raises(ValueError, match=f"Missing required field: {field}"):
        parse_target_event_form(urlencode(event_fields))


@pytest.mark.parametrize("field", ["event_type", "status"])
@pytest.mark.parametrize("value", ["", "unknown"])
def test_event_form_rejects_blank_or_invalid_enum_values(
    event_fields: dict[str, str], field: str, value: str
) -> None:
    event_fields[field] = value

    with pytest.raises(ValueError, match=f"Invalid {field}"):
        parse_target_event_form(urlencode(event_fields))


@pytest.mark.parametrize("name", ["", " \t\n "])
def test_event_form_leaves_blank_name_validation_to_the_domain(
    event_fields: dict[str, str], name: str
) -> None:
    event_fields["name"] = name

    values = parse_target_event_form(urlencode(event_fields))

    assert values.name == ""


def test_event_form_decodes_special_characters_and_trims_surrounding_text(
    event_fields: dict[str, str],
) -> None:
    event_fields["name"] = "  HYROX + running & café / 50%  "

    values = parse_target_event_form(urlencode(event_fields))

    assert values.name == "HYROX + running & café / 50%"


@pytest.mark.parametrize("field", ["title", "status", "target_date", "target_event_id"])
def test_goal_form_rejects_duplicate_single_value_fields(
    goal_fields: dict[str, str], field: str
) -> None:
    fields = goal_fields | {
        "target_date": "2030-05-01",
        "target_event_id": str(UUID(int=99)),
    }
    body = urlencode([*fields.items(), (field, fields[field])])

    with pytest.raises(ValueError, match=f"Duplicate field: {field}"):
        parse_goal_form(body)


@pytest.mark.parametrize("field", ["name", "event_date", "event_type", "status"])
def test_event_form_rejects_duplicate_single_value_fields(
    event_fields: dict[str, str], field: str
) -> None:
    body = urlencode([*event_fields.items(), (field, event_fields[field])])

    with pytest.raises(ValueError, match=f"Duplicate field: {field}"):
        parse_target_event_form(body)


def test_parsed_form_values_are_immutable(
    goal_fields: dict[str, str], event_fields: dict[str, str]
) -> None:
    goal_values = parse_goal_form(urlencode(goal_fields))
    event_values = parse_target_event_form(urlencode(event_fields))

    with pytest.raises(FrozenInstanceError):
        goal_values.title = "Changed"
    with pytest.raises(FrozenInstanceError):
        event_values.name = "Changed"
