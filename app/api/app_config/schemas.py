from datetime import date

from app.core.schemas import BaseSchema


class DayOffBase(BaseSchema):
    date: date
    description: str


class DayOffCreate(DayOffBase):
    pass


class DayOffResponse(DayOffBase):
    pass
