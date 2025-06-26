from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class GlobalConfig(BaseSchema):
    title: str = Field(examples=["Attendance Control API"])
    version: str = Field(examples=["0.1.0"])
    description: str = Field(examples=["The backend of the attendance control system"])
    root_path: str = Field(examples=[""])
    docs_url: str | None = Field(examples=["/docs"])
    redoc_url: str | None = Field(examples=["/redoc"])
    openapi_url: str | None = Field(examples=["/openapi.json"])
