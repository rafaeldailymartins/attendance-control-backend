from sqlmodel import Session

from app.api.app_config.schemas import DayOffCreate
from app.core.crud import db_insert
from app.core.models import DayOff


def create_day_off(session: Session, day_off_create: DayOffCreate):
    day_off = DayOff.model_validate(day_off_create)
    db_insert(session, day_off)
    return day_off
