from typing import Union
from pydantic import BaseModel, Field


class GlobalConfig(BaseModel):
    title: str = Field(examples=["Attendance Control API"])
    version: str = Field(examples=["0.1.0"])
    description: str = Field(examples=["The backend of the attendance control system"])
    root_path: str = Field(examples=[""])
    docs_url: Union[str, None] = Field(examples=["/docs"])
    redoc_url: Union[str, None] = Field(examples=["/redoc"])
    openapi_url: Union[str, None] = Field(examples=["/openapi.json"])
