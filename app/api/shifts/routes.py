from fastapi import APIRouter, Depends, status

from app.api.shifts import crud
from app.api.shifts.schemas import ShiftCreate, ShiftResponse, ShiftUpdate
from app.api.users import crud as users_crud
from app.core.crud import db_delete
from app.core.deps import SessionDep, check_admin
from app.core.exceptions import BaseHTTPException
from app.core.schemas import Message

router = APIRouter(prefix="/shifts", tags=["shifts"])


@router.post("/", response_model=ShiftResponse, dependencies=[Depends(check_admin)])
def create_new_shift(session: SessionDep, body: ShiftCreate):
    """
    Create new shift
    """
    user = users_crud.get_user_by_id(session=session, id=body.user_id)
    if not user:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Usuário não encontrado.",
        )
    shift_create = ShiftCreate.model_validate(body)
    shift = crud.create_shift(session=session, shift_create=shift_create)
    return shift


@router.patch(
    "/{shift_id}", response_model=ShiftResponse, dependencies=[Depends(check_admin)]
)
def update_shift(session: SessionDep, shift_id: int, body: ShiftUpdate):
    """
    Update a shift
    """
    if body.user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=body.user_id)
        if not user:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Usuário não encontrado.",
            )

    shift = crud.get_shift_by_id(session, shift_id)
    if not shift:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Turno não encontrado"
        )
    crud.update_shift(session, shift, body)
    return shift


@router.delete("/{shift_id}", dependencies=[Depends(check_admin)])
def delete_shift(session: SessionDep, shift_id: int) -> Message:
    """
    Delete a shift.
    """
    shift = crud.get_shift_by_id(session, shift_id)
    if not shift:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Turno não encontrado"
        )
    db_delete(session, shift)
    return Message(message="Turno deletado com sucesso")


@router.get(
    "/",
    response_model=list[ShiftResponse],
    dependencies=[Depends(check_admin)],
)
def list_shifts(session: SessionDep):
    """
    Get all shifts
    """
    shifts = crud.list_shifts(session)
    return shifts
