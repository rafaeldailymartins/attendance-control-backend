from datetime import date

from app.core.schemas import BaseSchema


class DayOffBase(BaseSchema):
    date: date
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
