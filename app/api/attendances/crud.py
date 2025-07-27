from datetime import UTC, datetime, timedelta

from sqlmodel import Session

from app.api.app_config import crud as app_config_crud
from app.core.crud import db_insert
from app.core.models import Attendance, AttendanceType, Shift


def get_minutes_late(
    session: Session,
    shift: Shift,
    type: AttendanceType,
    dt: datetime,
):
    app_config = app_config_crud.get_last_app_config(session)
    if not app_config:
        raise ValueError(
            "Ocorreu um erro no servidor e não foi possível encontrar as configurações."
        )

    delta = timedelta(minutes=0)

    if type == AttendanceType.CLOCK_IN:
        shift_start_datetime = datetime.combine(dt.date(), shift.start_time, tzinfo=UTC)
        delta = dt - shift_start_datetime
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_late else 0

    if type == AttendanceType.CLOCK_OUT:
        shift_end_datetime = datetime.combine(dt.date(), shift.end_time, tzinfo=UTC)
        delta = shift_end_datetime - dt
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_early else 0


def create_attendance(session: Session, shift: Shift, type: AttendanceType):
    now = datetime.now(UTC)
    minutes_late = get_minutes_late(session, shift, type, now)
    attendance = Attendance(
        datetime=now, minutes_late=minutes_late, type=type, shift_id=shift.id
    )
    db_insert(session, attendance)
    return attendance
