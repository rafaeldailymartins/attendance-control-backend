import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.core.config import settings
from app.api.core.schemas import GlobalConfig

app = FastAPI(
    title=settings.TITLE,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", tags=["main"], response_model=GlobalConfig)
def root():
    """
    Returns information about the application.
    """
    return app


@app.get("/health", tags=["main"])
def health_check() -> bool:
    """
    Checks if the application is running and healthy.
    """
    return True


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
