from fastapi import APIRouter, Depends

from app.api.shifts import crud
from app.api.shifts.schemas import ShiftCreate, ShiftResponse
from app.core.deps import SessionDep, check_admin

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.post("/", response_model=ShiftResponse, dependencies=[Depends(check_admin)])
def create_new_shift(session: SessionDep, body: ShiftCreate):
    """
    Create new shift
    """
    shift_create = ShiftCreate.model_validate(body)
    user = crud.create_shift(session=session, shift_create=shift_create)
    return user
