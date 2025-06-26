from datetime import date, datetime, time, timezone
from enum import IntEnum

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class ModelBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)


class Role(ModelBase, table=True):
    name: str = Field(unique=True)

    users: list["User"] = Relationship(back_populates="role")


class User(ModelBase, table=True):
    email: EmailStr = Field(unique=True, index=True)
    password: str
    name: str = Field(index=True)
    active: bool = Field(default=True)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    role_id: int | None = Field(
        default=None, foreign_key="role.id", nullable=True, ondelete="SET NULL"
    )

    role: Role | None = Relationship(back_populates="users")
    shifts: list["Shift"] = Relationship(back_populates="user")


class WeekdayEnum(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


class Shift(ModelBase, table=True):
    weekday: WeekdayEnum
    start_time: time
    end_time: time
    user_id: int = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    user: User = Relationship(back_populates="shifts")
    attendances: list["Attendance"] = Relationship(back_populates="shift")


class AttendanceType(IntEnum):
    CLOCK_IN = 0
    CLOCK_OUT = 1


class Attendance(ModelBase, table=True):
    datetime: datetime
    minutes_late: int
    type: AttendanceType
    shift_id: int = Field(foreign_key="shift.id", nullable=False, ondelete="CASCADE")

    shift: Shift = Relationship(back_populates="attendances")


class DayOff(ModelBase, table=True):
    date: date
    description: str


class AppConfig(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    minutes_late: int
    minutes_early: int
