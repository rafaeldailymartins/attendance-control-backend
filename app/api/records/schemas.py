from datetime import date, datetime

from pydantic import Field

from app.core.models import AttendanceType
from app.core.schemas import BaseSchema


class AttendanceBase(BaseSchema):
    attendance_type: AttendanceType = Field(
        description="The type of attendance. "
        "It can be 0 for clock in, or 1 for clock out."
    )
    shift_id: int = Field(description="The ID corresponding to the attendance's shift.")


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceResponse(AttendanceBase):
    id: int = Field(description="The attendance id.")
    timestamp: datetime = Field(description="The datetime of the attendance.")
    minutes_late: int = Field(
        description="The minutes the user was late clocking in or out. "
        "If it's less than the AppConfig setting (mintues_late for clock in "
        "and minutes_early for clock out), the value is saved as 0."
    )


class AttendanceUpdate(BaseSchema):
    attendance_type: AttendanceType | None = Field(
        default=None,
        description="The type of attendance. "
        "It can be 0 for clock in, or 1 for clock out.",
    )
    shift_id: int | None = Field(
        default=None, description="The ID corresponding to the attendance's shift."
    )
    timestamp: datetime | None = Field(
        default=None, description="The datetime of the attendance."
    )
    minutes_late: int | None = Field(
        default=None,
        description="The minutes the user was late clocking in or out. "
        "If it's less than the AppConfig setting (mintues_late for clock in "
        "and minutes_early for clock out), the value is saved as 0.",
    )


class AbsenceResponse(BaseSchema):
    shift_id: int = Field(description="The ID corresponding to the absence's shift.")
    day: date = Field(description="The date that attendance should have been recorded.")
    absence_type: AttendanceType = Field(
        description="The type of absence. It can be 0 for clock in, or 1 for clock out."
    )
    minutes_late: int | None = Field(
        default=None,
        description="The minutes the user was late clocking in or out. "
        "If the value is different from null, the presence was recorded, but late.",
    )
    attendance_timestamp: datetime | None = Field(
        default=None,
        description="The time the attendance was recorded. "
        "If the value is different from null, the presence was recorded, but late.",
    )


class ShiftDate(BaseSchema):
    day: date
    shift_id: int
