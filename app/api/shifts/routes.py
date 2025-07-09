from fastapi import APIRouter, Depends, status

from app.api.shifts import crud
from app.api.shifts.schemas import ShiftCreate, ShiftResponse
from app.api.users import crud as user_crud
from app.core.deps import SessionDep, check_admin
from app.core.exceptions import BaseHTTPException

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.post("/", response_model=ShiftResponse, dependencies=[Depends(check_admin)])
def create_new_shift(session: SessionDep, body: ShiftCreate):
    """
    Create new shift
    """
    user = user_crud.get_user_by_id(session=session, id=body.user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Usuário não encontrado.",
        )
    shift_create = ShiftCreate.model_validate(body)
    user = crud.create_shift(session=session, shift_create=shift_create)
    return user
