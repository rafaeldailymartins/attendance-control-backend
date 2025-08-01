from datetime import UTC, datetime

from sqlmodel import Session, select

from app.api.shifts.schemas import ShiftCreate, ShiftUpdate
from app.api.users import crud as users_crud
from app.core.crud import db_update
from app.core.models import AttendanceType, Shift, User


def create_shift(
    session: Session,
    shift_create: ShiftCreate,
    commit: bool = True,
    update_user: bool = True,
):
    shift = Shift.model_validate(shift_create)

    if update_user:
        user = update_user_timestamp(session, shift.user_id)
        shift.user = user

    session.add(shift)

    if commit:
        session.commit()
        session.refresh(shift)
    return shift


def get_shift_by_id(session: Session, id: int):
    return session.get(Shift, id)


def update_user_timestamp(session: Session, user_id: int):
    user = users_crud.get_user_by_id(session, user_id)
    user.updated_shifts_at = datetime.now()
    return user


def update_shift(session: Session, shift: Shift, shift_update: ShiftUpdate):
    user_id = shift.user_id
    if shift_update.user_id is not None:
        user_id = shift_update.user_id

    user = update_user_timestamp(session, user_id)
    shift.user = user

    shift_data = shift_update.model_dump(exclude_unset=True)
    db_update(session, shift, shift_data)
    return shift


def delete_shifts(session: Session, shifts: list[Shift], commit: bool = True):
    for shift in shifts:
        session.delete(shift)

    if commit:
        session.commit()


def list_shifts(session: Session, user_id: int | None = None):
    statement = select(Shift)

    if user_id is not None:
        statement = statement.where(Shift.user_id == user_id)

    return session.exec(statement).all()


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
