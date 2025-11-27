from datetime import time

from pydantic import EmailStr, Field, field_serializer

from app.core.models import WeekdayEnum
from app.core.schemas import BaseSchema


class ShiftBase(BaseSchema):
    weekday: WeekdayEnum = Field(
        description="An integer representing the day of the week, "
        "starting with 0 (Monday) and ending with 6 (Sunday)."
    )
    start_time: time = Field(description="The start time of the shift.")
    end_time: time = Field(description="The end time of the shift.")


class ShiftCreate(ShiftBase):
    user_id: int = Field(description="The ID corresponding to the shift's user.")


class ShiftUserResponse(BaseSchema):
    id: int = Field(description="The user id.")
    active: bool = Field(
        description="False if the user should be hidden when returning absences."
    )
    email: EmailStr = Field(
        description="The user's email, also used as the username when logging in."
    )
    name: str = Field(max_length=255, description="The user's full name.")
    role_id: int | None = Field(
        default=None, description="The ID corresponding to the user's role."
    )


class ShiftResponse(ShiftBase):
    id: int = Field(description="The shift id.")
    user_id: int = Field(description="The ID corresponding to the shift's user.")
    user: ShiftUserResponse

    @field_serializer("start_time", "end_time")
    def serialize_time(self, value: time):
        return value.replace(microsecond=0).isoformat()


class ShiftUpdate(BaseSchema):
    weekday: WeekdayEnum | None = Field(
        default=None,
        description="An integer representing the day of the week, "
        "starting with 0 (Monday) and ending with 6 (Sunday).",
    )
    start_time: time | None = Field(
        default=None, description="The start time of the shift."
    )
    end_time: time | None = Field(
        default=None, description="The end time of the shift."
    )
    user_id: int | None = Field(
        default=None, description="The ID corresponding to the shift's user."
    )


class UserCurrentShiftResponse(BaseSchema):
    message: str = Field(
        description="A message indicating whether the user's shift was returned."
    )
    shift: ShiftResponse | None = Field(
        description="The user's current shift. "
        "It is null if the user has no more shifts or if their shift could not be found"
    )
