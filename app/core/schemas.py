from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class GlobalConfig(BaseSchema):
    title: str = Field(
        examples=["Attendance Control API"], description="The title of the API."
    )
    version: str = Field(
        examples=["0.1.0"], description="The current version of the API."
    )
    description: str = Field(
        examples=["The backend of the attendance control system"],
        description="A short description of the API.",
    )
    root_path: str = Field(
        examples=[""],
        description="The root path of the application.",
    )
    docs_url: str | None = Field(
        examples=["/docs"],
        description="The URL to the Swagger UI documentation, if enabled.",
    )
    redoc_url: str | None = Field(
        examples=["/redoc"],
        description="The URL to the ReDoc documentation, if enabled.",
    )
    openapi_url: str | None = Field(
        examples=["/openapi.json"],
        description="The URL to the OpenAPI schema (JSON), if enabled.",
    )


class Token(BaseSchema):
    access_token: str = Field(
        description="A JWT token to be used in the `Authorization` header "
        "for authenticated requests."
    )
    token_type: str = Field(
        default="Bearer",
        description="The type of the token returned. "
        "Must be used in the `Authorization` header along with `accessToken` "
        "for authenticated requests.",
    )


class TokenPayload(BaseSchema):
    sub: str | None = None


class Message(BaseSchema):
    message: str


class PaginationParams(BaseSchema):
    page_size: int = Field(
        100, ge=1, le=100, description="Requested number of items per page"
    )
    page: int = Field(1, ge=1, description="Requested page number")


T = TypeVar("T", bound=BaseModel)


class Page[T](BaseSchema):
    items: list[T] = Field(description="List of items on this Page")
    total_items: int = Field(description="Number of total items")
    total_pages: int = Field(description="Total number of pages")
    current_page: int = Field(description="Page number")
    current_page_size: int = Field(description="Number of items per page")
