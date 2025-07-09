from pydantic import EmailStr, Field

from app.api.shifts.schemas import ShiftBase
from app.core.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=255)
    role_id: int | None = None


class UserShiftResponse(ShiftBase):
    id: int


class UserResponse(UserBase):
    id: int
    shifts: list[UserShiftResponse] = []


class UserShiftCreate(ShiftBase):
    pass


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=50)
    shifts: list[UserShiftCreate] = []


class UserUpdate(BaseSchema):
    name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=50)
    active: bool | None = None
    role_id: int | None = None
