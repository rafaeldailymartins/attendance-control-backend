from sqlmodel import Session, desc, select

from app.api.app_config.schemas import (
    AppConfigUpdate,
    DayOffCreate,
    RoleCreate,
    RoleUpdate,
)
from app.core.crud import db_insert, db_update
from app.core.models import AppConfig, DayOff, Role


def create_day_off(session: Session, day_off_create: DayOffCreate):
    day_off = DayOff.model_validate(day_off_create)
    db_insert(session, day_off)
    return day_off


def create_role(session: Session, role_create: RoleCreate):
    role = Role.model_validate(role_create)
    db_insert(session, role)
    return role


def get_role_by_name(session: Session, name: str):
    statement = select(Role).where(Role.name == name)
    session_role = session.exec(statement).first()
    return session_role


def get_role_by_id(session: Session, id: int):
    return session.get(Role, id)


def get_day_off_by_id(session: Session, id: int):
    return session.get(DayOff, id)


def get_last_app_config(session: Session):
    statement = select(AppConfig).order_by(desc(AppConfig.id))
    session_app_config = session.exec(statement).first()
    return session_app_config


def update_role(session: Session, role: Role, role_update: RoleUpdate):
    role_data = role_update.model_dump(exclude_unset=True)
    db_update(session, role, role_data)
    return role


def update_app_config(
    session: Session, app_config: AppConfig, app_config_update: AppConfigUpdate
):
    app_config_data = app_config_update.model_dump(exclude_unset=True)
    db_update(session, app_config, app_config_data)
    return app_config
