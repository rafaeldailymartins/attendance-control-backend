from pydantic import EmailStr, Field

from app.api.shifts.schemas import ShiftBase
from app.core.schemas import BaseSchema


class UserBase(BaseSchema):
    email: EmailStr = Field(
        max_length=255,
        description="The user's email, also used as the username when logging in.",
    )
    name: str = Field(max_length=255, description="The user's full name.")
    role_id: int | None = Field(
        default=None, description="The ID corresponding to the user's role."
    )


class UserShiftResponse(ShiftBase):
    id: int = Field(description="The shift id.")


class UserResponse(UserBase):
    id: int = Field(description="The user id.")
    shifts: list[UserShiftResponse] = Field(
        description="A list of UserShiftResponse schema, containing the user's shifts.",
    )


class UserShiftCreate(ShiftBase):
    pass


class UserCreate(UserBase):
    password: str = Field(
        min_length=8,
        max_length=50,
        description="The user's password. It must be between 8 and 50 characters long.",
    )
    shifts: list[UserShiftCreate] = Field(
        description="A list of UserShiftCreate schema, containing the user's shifts.",
    )


class UserUpdate(BaseSchema):
    name: str | None = Field(
        default=None, max_length=255, description="The user's full name."
    )
    email: EmailStr | None = Field(
        default=None,
        max_length=255,
        description="The user's email, also used as the username when logging in.",
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=50,
        description="The user's password. It must be between 8 and 50 characters long.",
    )
    active: bool | None = Field(
        default=None, description="Indicates whether the user is active."
    )
    role_id: int | None = Field(
        default=None, description="The ID corresponding to the user's role."
    )
    shifts: list[UserShiftCreate] | None = Field(
        default=None,
        description="A list of UserShiftCreate schema, containing the user's shifts.",
    )
