import uvicorn
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import app_config, attendances, shifts, users
from app.core.config import settings
from app.core.exceptions import BaseHTTPException, InternalServerErrorException
from app.core.schemas import GlobalConfig

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


@app.exception_handler(Exception)
async def custom_exception_handler():
    internal_exception = InternalServerErrorException(extra="Internal Server Error")
    return JSONResponse(
        status_code=internal_exception.status_code,
        content={"detail": internal_exception.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    base_exception = BaseHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Os dados enviados através da requisição não são válidos",
        extra=jsonable_encoder(exc.errors()),
    )
    return JSONResponse(
        status_code=base_exception.status_code,
        content={"detail": base_exception.detail},
    )


# Routes
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


app.include_router(users.router)
app.include_router(app_config.router)
app.include_router(shifts.router)
app.include_router(attendances.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
