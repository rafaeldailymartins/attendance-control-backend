from pydantic import EmailStr, Field

from app.core.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=255)


class UserResponse(UserBase):
    pass
