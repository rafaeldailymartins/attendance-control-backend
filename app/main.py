import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api import app_config, records, shifts, users
from app.core.config import settings
from app.core.schemas import ApiError, GlobalConfig

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    responses={500: {"model": ApiError}},
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Routes
@app.get("/", tags=["main"], response_model=GlobalConfig)
def root():
    """
    Get basic information about the application.
    """
    return app


@app.get("/health", tags=["main"])
def health_check() -> bool:
    """
    Checks if the application is running and healthy.
    """
    return True


app.include_router(users.router)
app.include_router(app_config.router)
app.include_router(shifts.router)
app.include_router(records.router)


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


use_route_names_as_operation_ids(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
