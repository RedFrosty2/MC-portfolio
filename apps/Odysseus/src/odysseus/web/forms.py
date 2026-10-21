"""Translate browser availability fields into production domain values."""

from urllib.parse import parse_qs

from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)


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
