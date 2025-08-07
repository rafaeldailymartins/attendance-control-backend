from collections import defaultdict
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.api.app_config import crud as app_config_crud
from app.api.attendances.schemas import AbsenceResponse, AttendanceUpdate, ShiftDate
from app.api.shifts import crud as shifts_crud
from app.core.crud import db_insert, db_update
from app.core.models import (
    AppConfig,
    Attendance,
    AttendanceType,
    Shift,
    User,
    WeekdayEnum,
)


def get_minutes_late(
    app_config: AppConfig,
    shift: Shift,
    attendance_type: AttendanceType,
    dt: datetime,
):
    zone_info = ZoneInfo(app_config.zone_info)
    delta = timedelta(minutes=0)

    if attendance_type == AttendanceType.CLOCK_IN:
        shift_start_datetime = datetime.combine(
            dt.date(), shift.start_time, tzinfo=zone_info
        )
        delta = dt - shift_start_datetime
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_late else 0

    if attendance_type == AttendanceType.CLOCK_OUT:
        shift_end_datetime = datetime.combine(
            dt.date(), shift.end_time, tzinfo=zone_info
        )
        delta = shift_end_datetime - dt
        minutes = int(delta.total_seconds() // 60)
        return max(minutes, 0) if minutes > app_config.minutes_early else 0


def create_attendance(session: Session, shift: Shift, attendance_type: AttendanceType):
    app_config = app_config_crud.get_last_app_config(session)
    if not app_config:
        raise ValueError(
            "Ocorreu um erro no servidor e não foi possível encontrar as configurações."
        )

    now = datetime.now(ZoneInfo(app_config.zone_info))
    minutes_late = get_minutes_late(app_config, shift, attendance_type, now)
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
    statement = select(Attendance).join(Shift).join(User)

    statement = statement.where(User.active)
    if user_id is not None:
        statement = statement.where(Shift.user_id == user_id)
    if attendance_type is not None:
        statement = statement.where(Attendance.attendance_type == attendance_type)
    if start_timestamp is not None:
        statement = statement.where(Attendance.timestamp >= start_timestamp)
    if end_timestamp is not None:
        statement = statement.where(Attendance.timestamp <= end_timestamp)

    return session.exec(statement).all()


def list_dates(start_date: date, end_date: date):
    return [
        start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)
    ]


def list_absences(
    session: Session,
    start_date: date,
    end_date: date,
    user_id: int | None = None,
    absence_type: AttendanceType | None = None,
):
    shifts = shifts_crud.list_shifts(session, user_id)

    shifts_by_weekday: defaultdict[WeekdayEnum, list[Shift]] = defaultdict(list[Shift])
    for shift in shifts:
        shifts_by_weekday[shift.weekday].append(shift)

    days_off = app_config_crud.list_days_off(
        session=session, start_date=start_date, end_date=end_date
    )

    dates = [
        dt
        for dt in list_dates(start_date, end_date)
        if dt not in [day_off.day for day_off in days_off]
    ]

    shift_dates: list[ShiftDate] = []

    for dt in dates:
        for shift in shifts:
            if (
                dt.weekday() == shift.weekday
                and dt >= shift.user.created_at.date()
                and (
                    shift.user.updated_shifts_at is None
                    or dt >= shift.user.updated_shifts_at.date()
                )
            ):
                shift_dates.append(ShiftDate(day=dt, shift_id=shift.id))

    attendances = list_attendances(
        session=session,
        start_timestamp=datetime.combine(start_date, time()),
        end_timestamp=datetime.combine(end_date, time()),
        attendance_type=absence_type,
        user_id=user_id,
    )

    absences: list[AbsenceResponse] = []
    for entry in shift_dates:
        clock_in_ids = [
            attendance.shift_id
            for attendance in attendances
            if entry.day == attendance.timestamp.date()
            and attendance.attendance_type == AttendanceType.CLOCK_IN
        ]
        clock_out_ids = [
            attendance.shift_id
            for attendance in attendances
            if entry.day == attendance.timestamp.date()
            and attendance.attendance_type == AttendanceType.CLOCK_OUT
        ]

        if entry.shift_id not in clock_in_ids and absence_type in (
            None,
            AttendanceType.CLOCK_IN,
        ):
            absences.append(
                AbsenceResponse(
                    shift_id=entry.shift_id,
                    day=entry.day,
                    absence_type=AttendanceType.CLOCK_IN,
                )
            )
        if entry.shift_id not in clock_out_ids and absence_type in (
            None,
            AttendanceType.CLOCK_OUT,
        ):
            absences.append(
                AbsenceResponse(
                    shift_id=entry.shift_id,
                    day=entry.day,
                    absence_type=AttendanceType.CLOCK_OUT,
                )
            )

    for attendance in attendances:
        if attendance.minutes_late > 0:
            absences.append(
                AbsenceResponse(
                    shift_id=attendance.shift_id,
                    day=attendance.timestamp.date(),
                    absence_type=attendance.attendance_type,
                    attendance_timestamp=attendance.timestamp,
                    minutes_late=attendance.minutes_late,
                )
            )

    return absences
