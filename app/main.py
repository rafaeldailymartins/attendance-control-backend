import uvicorn
from fastapi import FastAPI
from .core.config import settings
from .core.schemas import GlobalConfig

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
)


@app.get("/", tags=["root"], response_model=GlobalConfig)
async def root():
    """
    Returns information about the application.
    """
    return app


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
