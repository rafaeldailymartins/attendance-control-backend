from datetime import UTC, date, datetime, time
from enum import IntEnum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class ModelBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class Role(ModelBase, table=True):
    name: str = Field(unique=True, index=True)

    users: list["User"] = Relationship(back_populates="role")


class User(ModelBase, table=True):
    email: EmailStr = Field(unique=True, index=True)
    password: str
    name: str = Field(index=True)
    active: bool = Field(default=True)
    created_at: datetime = Field(default=datetime.now(UTC))
    updated_at: datetime | None = Field(default=None)
    role_id: int | None = Field(
        default=None, foreign_key="role.id", nullable=True, ondelete="SET NULL"
    )

    role: Role | None = Relationship(back_populates="users")
    shifts: list["Shift"] = Relationship(back_populates="user", passive_deletes=True)


class WeekdayEnum(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class Shift(ModelBase, table=True):
    weekday: WeekdayEnum
    start_time: time
    end_time: time
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    user: User = Relationship(back_populates="shifts")
    attendances: list["Attendance"] = Relationship(
        back_populates="shift", passive_deletes=True
    )


class AttendanceType(IntEnum):
    CLOCK_IN = 0
    CLOCK_OUT = 1


class Attendance(ModelBase, table=True):
    timestamp: datetime
    minutes_late: int
    attendance_type: AttendanceType
    shift_id: int = Field(foreign_key="shift.id", nullable=False, ondelete="CASCADE")

    shift: Shift = Relationship(back_populates="attendances")


class DayOff(ModelBase, table=True):
    day: date
    description: str


class AppConfig(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    minutes_late: int
    minutes_early: int
