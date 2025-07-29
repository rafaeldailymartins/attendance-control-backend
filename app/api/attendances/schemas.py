from datetime import date, datetime

from app.core.models import AttendanceType
from app.core.schemas import BaseSchema


class AttendanceBase(BaseSchema):
    attendance_type: AttendanceType
    shift_id: int


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int
    timestamp: datetime
    minutes_late: int


class AttendanceUpdate(BaseSchema):
    attendance_type: AttendanceType | None = None
    shift_id: int | None = None
    timestamp: datetime | None = None
    minutes_late: int | None = None


class AbsenceResponse(BaseSchema):
    shift_id: int
    day: date
    absence_type: AttendanceType
    minutes_late: int | None = None
    attendance_timestamp: datetime | None = None


class ShiftDate(BaseSchema):
    day: date
    shift_id: int
