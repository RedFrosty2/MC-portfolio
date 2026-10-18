from fastapi import FastAPI

from odysseus.application.availability import TrainingAvailabilityUseCases
from odysseus.web.routes.availability import create_availability_router


def create_app(use_cases: TrainingAvailabilityUseCases) -> FastAPI:
    app = FastAPI()
    app.include_router(create_availability_router(use_cases))
    return app
