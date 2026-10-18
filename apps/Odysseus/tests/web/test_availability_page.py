import re
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from odysseus.adapters.in_memory.availability import InMemoryTrainingAvailabilityStore
from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.domain.availability import (
    DailyTrainingAvailability,
    RecurringTrainingAvailability,
    Weekday,
)
from odysseus.web.app import create_app


@pytest.fixture
def use_cases() -> TrainingAvailabilityUseCases:
    availability = RecurringTrainingAvailability(
        days=(
            DailyTrainingAvailability(Weekday.SUNDAY, False, False, True),
            DailyTrainingAvailability(Weekday.SATURDAY, False, True, False),
            DailyTrainingAvailability(Weekday.FRIDAY, True, False, False),
            DailyTrainingAvailability(Weekday.THURSDAY, False, False, False),
            DailyTrainingAvailability(Weekday.WEDNESDAY, True, True, False),
            DailyTrainingAvailability(Weekday.TUESDAY, False, True, False),
            DailyTrainingAvailability(Weekday.MONDAY, True, False, False),
        )
    )
    store = InMemoryTrainingAvailabilityStore(availability)
    return TrainingAvailabilityUseCases(store)


@pytest.fixture
def client(use_cases: TrainingAvailabilityUseCases) -> Iterator[TestClient]:
    with TestClient(create_app(use_cases)) as test_client:
        yield test_client


def rendered_day_cells(html: str, weekday_label: str) -> list[str]:
    row = re.search(
        rf'<tr>\s*<th scope="row">{weekday_label}</th>.*?</tr>',
        html,
        re.DOTALL,
    )
    assert row is not None
    cells = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row.group(0), re.DOTALL)
    return [" ".join(re.sub(r"<[^>]+>", "", cell).split()) for cell in cells]


def checked_fields(html: str) -> set[str]:
    return set(re.findall(r'<input\b[^>]*name="([^"]+)"[^>]*\bchecked\b[^>]*>', html))


def test_get_availability_returns_an_html_page(client: TestClient) -> None:
    response = client.get("/availability")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")


def test_page_renders_all_weekday_labels_in_monday_to_sunday_order(
    client: TestClient,
) -> None:
    response = client.get("/availability")

    assert re.findall(r'<th scope="row">([^<]+)</th>', response.text) == [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]


@pytest.mark.parametrize(
    "weekday_label, am_label, pm_label, day_status",
    [
        ("Monday", "AM available", "PM unavailable", "Available"),
        ("Tuesday", "AM unavailable", "PM available", "Available"),
        ("Thursday", "AM unavailable", "PM unavailable", "Unavailable"),
        ("Sunday", "AM unavailable", "PM unavailable", "REST"),
    ],
)
def test_page_distinguishes_training_rest_and_unavailable_days(
    client: TestClient,
    weekday_label: str,
    am_label: str,
    pm_label: str,
    day_status: str,
) -> None:
    response = client.get("/availability")

    assert rendered_day_cells(response.text, weekday_label) == [
        weekday_label,
        am_label,
        pm_label,
        "REST",
        day_status,
    ]


def test_page_has_a_post_form_with_current_checkbox_values(client: TestClient) -> None:
    response = client.get("/availability")

    assert re.search(r'<form method="post" action="[^"]*/availability">', response.text)
    assert len(re.findall(r'<input type="checkbox"', response.text)) == 21
    assert checked_fields(response.text) == {
        "monday_am",
        "tuesday_pm",
        "wednesday_am",
        "wednesday_pm",
        "friday_am",
        "saturday_pm",
        "sunday_rest",
    }


def test_valid_post_redirects_to_get_availability(client: TestClient) -> None:
    response = client.post(
        "/availability", data={"monday_pm": "on"}, follow_redirects=False
    )

    assert response.status_code == 303
    assert response.headers["location"] == "http://testserver/availability"


def test_redirected_page_displays_updated_training_rest_and_unavailable_days(
    client: TestClient,
) -> None:
    fields = {
        "monday_pm": "on",
        "tuesday_am": "on",
        "friday_rest": "on",
        "saturday_am": "on",
        "saturday_pm": "on",
    }

    response = client.post("/availability", data=fields)

    assert response.status_code == 200
    assert [redirect.status_code for redirect in response.history] == [303]
    assert response.request.method == "GET"
    assert response.url.path == "/availability"
    assert checked_fields(response.text) == set(fields)
    assert rendered_day_cells(response.text, "Monday") == [
        "Monday",
        "AM unavailable",
        "PM available",
        "REST",
        "Available",
    ]
    assert rendered_day_cells(response.text, "Tuesday") == [
        "Tuesday",
        "AM available",
        "PM unavailable",
        "REST",
        "Available",
    ]
    assert rendered_day_cells(response.text, "Friday")[-1] == "REST"
    assert rendered_day_cells(response.text, "Sunday")[-1] == "Unavailable"


def test_all_unchecked_fields_save_an_ordinary_unavailable_week(
    client: TestClient,
) -> None:
    response = client.post(
        "/availability",
        content="",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200
    assert checked_fields(response.text) == set()
    for weekday in Weekday:
        assert rendered_day_cells(response.text, weekday.value.capitalize())[-1] == (
            "Unavailable"
        )


@pytest.mark.parametrize(
    "training_fields",
    [
        {"sunday_am": "on"},
        {"sunday_pm": "on"},
        {"sunday_am": "on", "sunday_pm": "on"},
    ],
)
def test_invalid_rest_submission_reports_error_and_preserves_the_stored_week(
    client: TestClient,
    use_cases: TrainingAvailabilityUseCases,
    training_fields: dict[str, str],
) -> None:
    previous_week = use_cases.get_recurring_availability()
    previous_page = client.get("/availability").text

    response = client.post(
        "/availability",
        data={"monday_pm": "on", "sunday_rest": "on", **training_fields},
    )

    assert response.status_code == 422
    assert "Invalid training availability" in response.json()["detail"]
    assert "rest day" in response.json()["detail"]
    assert use_cases.get_recurring_availability() is previous_week
    assert client.get("/availability").text == previous_page


def test_non_form_submission_is_rejected_without_replacing_the_week(
    client: TestClient,
    use_cases: TrainingAvailabilityUseCases,
) -> None:
    previous_week = use_cases.get_recurring_availability()

    response = client.post("/availability", json={"monday_pm": "on"})

    assert response.status_code == 415
    assert "URL-encoded form" in response.json()["detail"]
    assert use_cases.get_recurring_availability() is previous_week
