from pydantic import EmailStr, Field

from app.core.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=255)


class UserResponse(UserBase):
    id: int


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=50)


class UserUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=50)
