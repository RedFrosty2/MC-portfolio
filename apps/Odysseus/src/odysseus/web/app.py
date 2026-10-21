"""Assemble the FastAPI web boundary around injected application operations."""

from fastapi import FastAPI

from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.web.routes.availability import create_availability_router


def create_app(use_cases: TrainingAvailabilityUseCases) -> FastAPI:
    """Create an application with the availability HTTP routes registered.

    Args:
        use_cases: Application collaborator shared by the route handlers. Its
            storage dependency is supplied outside the web layer.

    Returns:
        A FastAPI application; this factory does not construct storage or start
        a server.
    """
    app = FastAPI()
    app.include_router(create_availability_router(use_cases))
    return app
