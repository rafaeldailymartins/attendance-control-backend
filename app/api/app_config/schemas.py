from datetime import date
from zoneinfo import ZoneInfo

from app.core.schemas import BaseSchema


class DayOffBase(BaseSchema):
    day: date
    description: str


class DayOffCreate(DayOffBase):
    pass


class DayOffResponse(DayOffBase):
    id: int


class RoleBase(BaseSchema):
    name: str


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: int


class RoleUpdate(BaseSchema):
    name: str | None = None


class AppConfigBase(BaseSchema):
    minutes_late: int
    minutes_early: int
    zone_info: str


class AppConfigResponse(AppConfigBase):
    id: int


class AppConfigUpdate(BaseSchema):
    minutes_late: int | None = None
    minutes_early: int | None = None
    zone_info: ZoneInfo | None = None


class TimezoneResponse(BaseSchema):
    zone_info: str
    offset: str
