from datetime import UTC, datetime
from zoneinfo import ZoneInfo, available_timezones

from sqlmodel import Session, desc, select

from app.api.app_config.schemas import (
    AppConfigUpdate,
    DayOffCreate,
    RoleCreate,
    RoleUpdate,
    TimezoneResponse,
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


def list_days_off(session: Session):
    return session.exec(select(DayOff)).all()


def list_roles(session: Session):
    return session.exec(select(Role)).all()


def list_timezones() -> list[TimezoneResponse]:
    reference_dt = datetime.now(UTC)
    timezones_with_offsets: list[TimezoneResponse] = []

    for tz_name in sorted(available_timezones()):
        try:
            tz = ZoneInfo(tz_name)
            offset_timedelta = reference_dt.astimezone(tz).utcoffset()
            if offset_timedelta is not None:
                total_minutes = int(offset_timedelta.total_seconds() / 60)
                hours, minutes = divmod(abs(total_minutes), 60)
                sign = "+" if total_minutes >= 0 else "-"
                offset_str = f"{sign}{hours:02}:{minutes:02}"
            else:
                offset_str = "±00:00"

            timezones_with_offsets.append(
                TimezoneResponse(zone_info=tz_name, offset=offset_str)
            )
        except Exception:
            continue

    return timezones_with_offsets


def update_role(session: Session, role: Role, role_update: RoleUpdate):
    role_data = role_update.model_dump(exclude_unset=True)
    db_update(session, role, role_data)
    return role


def update_app_config(
    session: Session, app_config: AppConfig, app_config_update: AppConfigUpdate
):
    app_config_data = app_config_update.model_dump(exclude_unset=True)
    app_config_data["zone_info"] = app_config_data["zone_info"].key
    db_update(session, app_config, app_config_data)
    return app_config
