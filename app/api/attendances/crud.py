from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.api.app_config import crud as app_config_crud
from app.api.attendances.schemas import AttendanceUpdate
from app.core.crud import db_insert, db_update
from app.core.models import Attendance, AttendanceType, Shift


def get_minutes_late(
    session: Session,
    shift: Shift,
    attendance_type: AttendanceType,
    dt: datetime,
):
    app_config = app_config_crud.get_last_app_config(session)
    if not app_config:
        raise ValueError(
            "Ocorreu um erro no servidor e não foi possível encontrar as configurações."
        )

    delta = timedelta(minutes=0)

    if attendance_type == AttendanceType.CLOCK_IN:
        shift_start_datetime = datetime.combine(dt.date(), shift.start_time, tzinfo=UTC)
        delta = dt - shift_start_datetime
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_late else 0

    if attendance_type == AttendanceType.CLOCK_OUT:
        shift_end_datetime = datetime.combine(dt.date(), shift.end_time, tzinfo=UTC)
        delta = shift_end_datetime - dt
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_early else 0


def create_attendance(session: Session, shift: Shift, attendance_type: AttendanceType):
    now = datetime.now(UTC)
    minutes_late = get_minutes_late(session, shift, attendance_type, now)
    attendance = Attendance(
        timestamp=now,
        minutes_late=minutes_late,
        attendance_type=attendance_type,
        shift_id=shift.id,
    )
    db_insert(session, attendance)
    return attendance


def get_attendance_by_id(session: Session, id: int):
    return session.get(Attendance, id)


def update_attendance(
    session: Session, attendance: Attendance, attendance_update: AttendanceUpdate
):
    attendance_data = attendance_update.model_dump(exclude_unset=True)
    db_update(session, attendance, attendance_data)
    return attendance


def list_attendances(
    session: Session,
    user_id: int | None = None,
    attendance_type: AttendanceType | None = None,
    start_timestamp: datetime | None = None,
    end_timestamp: datetime | None = None,
):
    statement = select(Attendance).join(Shift)

    if user_id is not None:
        statement = statement.where(Shift.user_id == user_id)
    if attendance_type is not None:
        statement = statement.where(Attendance.attendance_type == attendance_type)
    if start_timestamp is not None:
        statement = statement.where(Attendance.timestamp >= start_timestamp)
    if end_timestamp is not None:
        statement = statement.where(Attendance.timestamp <= end_timestamp)

    return session.exec(statement).all()
