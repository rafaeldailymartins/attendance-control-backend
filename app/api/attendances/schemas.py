from datetime import datetime

from app.core.models import AttendanceType
from app.core.schemas import BaseSchema


class AttendanceBase(BaseSchema):
    type: AttendanceType
    shift_id: int


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    datetime: datetime
    minutes_late: int


class AttendanceUpdate(BaseSchema):
    type: AttendanceType | None
    shift_id: int | None
    datetime: datetime | None
    minutes_late: int | None
