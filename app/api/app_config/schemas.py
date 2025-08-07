from datetime import date
from zoneinfo import ZoneInfo

from pydantic import Field

from app.core.schemas import BaseSchema


class DayOffBase(BaseSchema):
    day: date = Field(description="The day off")
    description: str = Field(description="The day off description")


class DayOffCreate(DayOffBase):
    pass


class DayOffResponse(DayOffBase):
    id: int = Field(description="The day off id")


class RoleBase(BaseSchema):
    name: str = Field(description="The role name")


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int = Field(description="The role id")


class RoleUpdate(BaseSchema):
    name: str | None = Field(default=None, description="The role name")


class AppConfigBase(BaseSchema):
    minutes_late: int = Field(
        description="Number of minutes of tolerance to record the clock-in. "
        "If the attendance time minus the start of the shift is "
        "greater than this number, an absence will be recorded."
    )
    minutes_early: int = Field(
        description="Number of minutes of tolerance to record the clock-out. "
        "If the end of the shift minus the attendance time is "
        "greater than this number, an absence will be recorded."
    )
    zone_info: str = Field(
        description="IANA time zone string used as the system's default time zone.",
        examples=["America/Sao_Paulo"],
    )


class AppConfigResponse(AppConfigBase):
    id: int = Field(description="The app config id")


class AppConfigUpdate(BaseSchema):
    minutes_late: int | None = Field(
        default=None,
        description="Number of minutes of tolerance to record the clock-in. "
        "If the attendance time minus the start of the shift is "
        "greater than this number, an absence will be recorded.",
    )
    minutes_early: int | None = Field(
        default=None,
        description="Number of minutes of tolerance to record the clock-out. "
        "If the end of the shift minus the attendance time is "
        "greater than this number, an absence will be recorded.",
    )
    zone_info: ZoneInfo | None = Field(
        default=None,
        description="IANA time zone string used as the system's default time zone.",
        examples=["America/Sao_Paulo"],
    )


class TimezoneResponse(BaseSchema):
    zone_info: str = Field(
        description="IANA time zone string used as the system's default time zone.",
        examples=["America/Sao_Paulo"],
    )
    offset: str = Field(
        description="UTC offset corresponding to the selected time zone, "
        "in the format ±HH:MM",
        examples=["-03:00"],
    )
