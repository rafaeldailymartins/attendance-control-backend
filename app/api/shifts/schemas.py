from datetime import time

from app.core.models import WeekdayEnum
from app.core.schemas import BaseSchema


class ShiftBase(BaseSchema):
    weekday: WeekdayEnum
    start_time: time
    end_time: time


class ShiftCreate(ShiftBase):
    user_id: int


class ShiftResponse(ShiftBase):
    id: int
    user_id: int


class ShiftUpdate(BaseSchema):
    weekday: WeekdayEnum | None = None
    start_time: time | None = None
    end_time: time | None = None
    user_id: int | None = None
