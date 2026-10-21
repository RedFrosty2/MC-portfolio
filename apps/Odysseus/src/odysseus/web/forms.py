"""Translate browser fields into availability or typed goal/event form values."""

from dataclasses import dataclass
from datetime import date
from urllib.parse import parse_qs
from uuid import UUID

from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)
from odysseus.domain.goals import GoalStatus
from odysseus.domain.target_events import TargetEventStatus, TargetEventType


@dataclass(frozen=True)
class GoalFormValues:
    """Parsed goal fields without entity identity or relationship validation.

    A blank title remains subject to domain validation. The event UUID is an
    optional reference, not the new goal's identity.
    """

    title: str
    status: GoalStatus
    target_date: date | None
    target_event_id: UUID | None


@dataclass(frozen=True)
class TargetEventFormValues:
    """Parsed event fields without identity or domain name validation.

    Historical dates are allowed. These values apply to both creation and
    editing; identity comes from the application or route path respectively.
    """

    name: str
    event_date: date
    event_type: TargetEventType
    status: TargetEventStatus


def parse_training_availability_form(body: str) -> RecurringTrainingAvailability:
    """Construct a complete week from URL-encoded checkbox presence.

    Names follow the weekday_am, weekday_pm, and weekday_rest convention.
    A present name is true regardless of its submitted text; omitted names
    are false, so an empty form represents ordinary unavailability all week.
    Domain constructors, rather than this parser, own rest/availability rules.

    Args:
        body: The decoded application/x-www-form-urlencoded request body.

    Returns:
        A complete domain week in Monday-to-Sunday order.

    Raises:
        ValueError: If the constructed values violate a domain invariant.
    """
    fields = parse_qs(body, keep_blank_values=True)
    return RecurringTrainingAvailability(
        days=tuple(
            DailyTrainingAvailability(
                weekday=weekday,
                am_available=f"{weekday.value}_am" in fields,
                pm_available=f"{weekday.value}_pm" in fields,
                is_rest_day=f"{weekday.value}_rest" in fields,
            )
            for weekday in Weekday
        )
    )


def parse_goal_form(body: str) -> GoalFormValues:
    """Parse one URL-encoded goal submission without constructing an entity.

    Args:
        body: Decoded form body with title, status, and optional target_date
            and target_event_id. Omitted or blank optional fields become None.

    Returns:
        Typed values with surrounding title whitespace removed. Blank titles
        remain for the domain to validate; event relationships are not checked.

    Raises:
        ValueError: If a required field is absent, a recognized field is
            duplicated, or a status, HTML date, or UUID cannot be parsed.
    """
    fields = parse_qs(body, keep_blank_values=True)
    for field in ("title", "status", "target_date", "target_event_id"):
        if len(fields.get(field, ())) > 1:
            raise ValueError(f"Duplicate field: {field}.")
    for field in ("title", "status"):
        if field not in fields:
            raise ValueError(f"Missing required field: {field}.")

    try:
        status = GoalStatus(fields["status"][0])
    except ValueError as exc:
        raise ValueError(
            "Invalid status: use active, completed, cancelled, or inactive."
        ) from exc

    target_date_text = fields.get("target_date", [""])[0]
    target_date = (
        _parse_html_date(target_date_text, "target_date")
        if target_date_text.strip()
        else None
    )
    target_event_text = fields.get("target_event_id", [""])[0].strip()
    try:
        target_event_id = UUID(target_event_text) if target_event_text else None
    except ValueError as exc:
        raise ValueError("Invalid target_event_id: expected a UUID.") from exc

    return GoalFormValues(
        title=fields["title"][0].strip(),
        status=status,
        target_date=target_date,
        target_event_id=target_event_id,
    )


def parse_target_event_form(body: str) -> TargetEventFormValues:
    """Parse one URL-encoded event submission, accepting historical dates.

    Args:
        body: Decoded form body containing name, event_date, event_type, and
            status. Dates must use the HTML YYYY-MM-DD format.

    Returns:
        Typed values with surrounding name whitespace removed. A blank name
        remains subject to domain validation; no entity identity is generated.

    Raises:
        ValueError: If a required field is absent or duplicated, the date is
            blank or invalid, or an enum value is invalid.
    """
    fields = parse_qs(body, keep_blank_values=True)
    for field in ("name", "event_date", "event_type", "status"):
        if len(fields.get(field, ())) > 1:
            raise ValueError(f"Duplicate field: {field}.")
        if field not in fields:
            raise ValueError(f"Missing required field: {field}.")

    event_date = _parse_html_date(fields["event_date"][0], "event_date")
    try:
        event_type = TargetEventType(fields["event_type"][0])
    except ValueError as exc:
        raise ValueError(
            "Invalid event_type: use running, hyrox, strength, or other."
        ) from exc
    try:
        status = TargetEventStatus(fields["status"][0])
    except ValueError as exc:
        raise ValueError(
            "Invalid status: use active, completed, cancelled, or inactive."
        ) from exc

    return TargetEventFormValues(
        name=fields["name"][0].strip(),
        event_date=event_date,
        event_type=event_type,
        status=status,
    )


def _parse_html_date(value: str, field: str) -> date:
    """Parse a calendar date and report the field if HTML date syntax is invalid."""
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: expected YYYY-MM-DD.") from exc
    # fromisoformat also accepts compact and week dates, unlike an HTML date input.
    if parsed.isoformat() != value:
        raise ValueError(f"Invalid {field}: expected YYYY-MM-DD.")
    return parsed
