from sqlmodel import Session

from app.api.shifts.schemas import ShiftCreate
from app.core.models import Shift


def create_shift(session: Session, shift_create: ShiftCreate, commit: bool = True):
    shift = Shift.model_validate(shift_create)
    session.add(shift)
    if commit:
        session.commit()
        session.refresh(shift)
    return shift
