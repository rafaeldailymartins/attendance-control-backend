import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.api import app_config, records, shifts, users
from app.core.config import settings
from app.core.exceptions import BaseHTTPException
from app.core.schemas import ApiError, ApiErrorDetail, GlobalConfig

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


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, _: Exception):
    detail = ApiErrorDetail(message="Erro interno no servidor", metadata=None)
    content = ApiError(detail=detail)

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=content.model_dump()
    )

    # Since the CORSMiddleware is not executed when an unhandled server exception
    # occurs, we need to manually set the CORS headers ourselves if we want the FE
    # to receive a proper JSON 500, opposed to a CORS error.
    # Setting CORS headers on server errors is a bit of a philosophical topic of
    # discussion in many frameworks, and it is currently not handled in FastAPI.
    origin = request.headers.get("origin")

    if origin:
        # Have the middleware do the heavy lifting for us to parse
        # all the config, then update our response headers
        cors = CORSMiddleware(
            app=app,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Logic directly from Starlette's CORSMiddleware:
        # https://github.com/encode/starlette/blob/master/starlette/middleware/cors.py#L152

        response.headers.update(cors.simple_headers)
        has_cookie = "cookie" in request.headers

        # If request includes any cookie headers, then we must respond
        # with the specific origin instead of '*'.
        if cors.allow_all_origins and has_cookie:
            response.headers["Access-Control-Allow-Origin"] = origin

        # If we only allow specific origins, then we have to mirror back
        # the Origin header in the response.
        elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add_vary_header("Origin")

    return response


@app.exception_handler(BaseHTTPException)
async def custom_http_exception_handler(_, exc: BaseHTTPException):
    detail = ApiErrorDetail(message=exc.message, metadata=exc.metadata)
    content = ApiError(detail=detail)
    return JSONResponse(status_code=exc.status_code, content=content.model_dump())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError):
    detail = ApiErrorDetail(
        message="Os dados enviados são inválidos",
        metadata=jsonable_encoder(exc.errors()),
    )
    content = ApiError(detail=detail)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=content.model_dump(),
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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )
    http_methods = ["post", "get", "put", "patch", "delete"]

    # look for the error 422 and removes it
    for path in openapi_schema["paths"]:
        for method in http_methods:
            try:
                del openapi_schema["paths"][path][method]["responses"]["422"]
            except KeyError:
                pass

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
