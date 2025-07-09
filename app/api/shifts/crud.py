from sqlmodel import Session, select

from app.api.shifts.schemas import ShiftCreate, ShiftUpdate
from app.core.crud import db_update
from app.core.models import Shift


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


def clean_user_shifts(session: Session, user_id: int, commit: bool = True):
    statement = select(Shift).where(Shift.user_id == user_id)
    shifts = session.exec(statement)

    for shift in shifts:
        session.delete(shift)

    if commit:
        session.commit()
