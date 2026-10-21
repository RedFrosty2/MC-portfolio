"""Coordinate availability HTML reads and form updates at the HTTP boundary."""

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.web.forms import parse_training_availability_form
from odysseus.web.presentation.availability import build_training_availability_view


def create_availability_router(use_cases: TrainingAvailabilityUseCases) -> APIRouter:
    """Bind availability handlers to an injected application collaborator.

    Templates are resolved relative to this package, independent of the
    process working directory. No concrete storage adapter is constructed.

    Returns:
        A router for GET rendering and POST updates followed by a GET redirect.
    """
    router = APIRouter()
    templates = Jinja2Templates(
        directory=Path(__file__).resolve().parent.parent / "templates"
    )

    @router.get("/availability", response_class=HTMLResponse)
    def get_availability(request: Request) -> HTMLResponse:
        """Load the current domain week and render its prepared presentation View."""
        availability = use_cases.get_recurring_availability()
        view = build_training_availability_view(availability)
        return templates.TemplateResponse(
            request=request,
            name="availability.html",
            context={"availability": view},
        )

    @router.post("/availability", response_class=RedirectResponse)
    async def update_availability(request: Request) -> RedirectResponse:
        """Replace the submitted week through the use case and redirect with 303.

        Only URL-encoded forms are accepted. Invalid construction is translated
        into a client response before the update use case is called; successful
        updates use POST/Redirect/GET to avoid refresh resubmission.

        Raises:
            HTTPException: With status 415 for unsupported content types, or
                422 for invalid UTF-8 or domain values. Neither case saves.
        """
        content_type = request.headers.get("content-type", "").split(";")[0].strip()
        if content_type.lower() != "application/x-www-form-urlencoded":
            raise HTTPException(status_code=415, detail="Submit a URL-encoded form.")

        body = await request.body()
        # Keep construction errors local; storage/application failures
        # must stay visible.
        try:
            availability = parse_training_availability_form(body.decode("utf-8"))
        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid training availability: {exc}",
            ) from exc

        use_cases.update_recurring_availability(availability)
        return RedirectResponse(
            url=request.url_for("get_availability"), status_code=303
        )

    return router
