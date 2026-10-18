from urllib.parse import parse_qs

from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)


def parse_training_availability_form(body: str) -> RecurringTrainingAvailability:
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
