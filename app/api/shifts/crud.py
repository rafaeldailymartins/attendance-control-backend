from sqlmodel import Session

from app.api.shifts.schemas import ShiftCreate
from app.core.crud import db_insert
from app.core.models import Shift


def create_shift(session: Session, shift_create: ShiftCreate):
    shift = Shift.model_validate(shift_create)
    db_insert(session, shift)
    return shift
