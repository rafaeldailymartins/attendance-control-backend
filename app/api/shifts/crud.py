from datetime import UTC, datetime

from sqlmodel import Session, select

from app.api.shifts.schemas import ShiftCreate, ShiftUpdate
from app.core.crud import db_update
from app.core.models import AttendanceType, Shift, User


def create_shift(session: Session, shift_create: ShiftCreate, commit: bool = True):
    shift = Shift.model_validate(shift_create)
    session.add(shift)
    if commit:
        session.commit()
        session.refresh(shift)
    return shift


def get_shift_by_id(session: Session, id: int):
    return session.get(Shift, id)


def update_shift(session: Session, shift: Shift, shift_update: ShiftUpdate):
    shift_data = shift_update.model_dump(exclude_unset=True)
    db_update(session, shift, shift_data)
    return shift


def delete_shifts(session: Session, shifts: list[Shift], commit: bool = True):
    for shift in shifts:
        session.delete(shift)

    if commit:
        session.commit()


def list_shifts(session: Session):
    return session.exec(select(Shift)).all()


def get_current_shift(user: User, attendance_type: AttendanceType) -> Shift | None:
    now = datetime.now(UTC)
    time_now = now.time()
    weekday = now.weekday()
    shifts = [shift for shift in user.shifts if shift.weekday == weekday]

    if attendance_type == AttendanceType.CLOCK_IN:
        shifts_sorted = sorted(shifts, key=lambda shift: shift.end_time)
        next_shift = next(
            (shift for shift in shifts_sorted if shift.end_time > time_now), None
        )
        return next_shift

    if attendance_type == AttendanceType.CLOCK_OUT:
        shifts_sorted = sorted(shifts, key=lambda shift: shift.start_time, reverse=True)
        next_shift = next(
            (shift for shift in shifts_sorted if shift.start_time < time_now), None
        )
        return next_shift
