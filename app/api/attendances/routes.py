from fastapi import APIRouter, Depends, status

from app.api.attendances import crud
from app.api.attendances.schemas import (
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.api.shifts import crud as shifts_crud
from app.core.config import settings
from app.core.crud import db_delete
from app.core.deps import CurrentUserDep, SessionDep, check_admin
from app.core.exceptions import BaseHTTPException, ForbiddenException
from app.core.schemas import Message

router = APIRouter(prefix="/attendances", tags=["attendances"])


@router.post("/", response_model=AttendanceResponse)
def create_new_attendance(
    session: SessionDep, body: AttendanceCreate, current_user: CurrentUserDep
):
    """
    Create new attendance (Clock in or Clock out)
    """
    shift = shifts_crud.get_shift_by_id(session, body.shift_id)
    if not shift:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Turno não encontrado.",
        )

    is_admin = (
        current_user.role is not None
        and current_user.role.name == settings.ADMIN_ROLE_NAME
    )
    is_allowed = shift.user_id == current_user.id or is_admin

    if not is_allowed:
        raise ForbiddenException()

    attendance = crud.create_attendance(session=session, shift=shift, type=body.type)
    return attendance


@router.patch(
    "/{attendance_id}",
    response_model=AttendanceResponse,
    dependencies=[Depends(check_admin)],
)
def update_attendance(session: SessionDep, attendance_id: int, body: AttendanceUpdate):
    """
    Update a attendance
    """
    if body.shift_id is not None:
        shift = shifts_crud.get_shift_by_id(session=session, id=body.shift_id)
        if not shift:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Turno não encontrado.",
            )

    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Registro não encontrado"
        )
    crud.update_attendance(session, attendance, body)
    return attendance


@router.delete("/{attendance_id}", dependencies=[Depends(check_admin)])
def delete_attendance(session: SessionDep, attendance_id: int) -> Message:
    """
    Delete a attendance.
    """
    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Registro não encontrado"
        )
    db_delete(session, attendance)
    return Message(message="Registro deletado com sucesso")
