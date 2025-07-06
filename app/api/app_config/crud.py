from sqlmodel import Session

from app.api.app_config.schemas import DayOffCreate, RoleCreate
from app.core.crud import db_insert
from app.core.models import DayOff, Role


def create_day_off(session: Session, day_off_create: DayOffCreate):
    day_off = DayOff.model_validate(day_off_create)
    db_insert(session, day_off)
    return day_off


def create_role(session: Session, role_create: RoleCreate):
    role = Role.model_validate(role_create)
    db_insert(session, role)
    return role
