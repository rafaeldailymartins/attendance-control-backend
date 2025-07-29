from datetime import date, datetime

from fastapi import APIRouter, Depends, status

from app.api.attendances import crud
from app.api.attendances.schemas import (
    AbsenceResponse,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.api.shifts import crud as shifts_crud
from app.api.users import crud as users_crud
from app.core.config import settings
from app.core.crud import db_delete
from app.core.deps import CurrentUserDep, SessionDep, check_admin
from app.core.exceptions import BaseHTTPException, ForbiddenException
from app.core.models import AttendanceType
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

    attendance = crud.create_attendance(
        session=session, shift=shift, attendance_type=body.attendance_type
    )
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


@router.get("/", response_model=list[AttendanceResponse])
def list_attendances(
    session: SessionDep,
    user_id: int | None = None,
    attendance_type: AttendanceType | None = None,
    start_timestamp: datetime | None = None,
    end_timestamp: datetime | None = None,
):
    """
    List attendances
    """
    if user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=user_id)
        if not user:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Usuário não encontrado.",
            )

    attendances = crud.list_attendances(
        session=session,
        user_id=user_id,
        attendance_type=attendance_type,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )
    return attendances


@router.get(
    "/absences",
    response_model=list[AbsenceResponse],
)
def list_absences(
    session: SessionDep,
    current_user: CurrentUserDep,
    start_date: date,
    end_date: date,
    user_id: int | None = None,
    absence_type: AttendanceType | None = None,
):
    """
    List absences
    """

    is_admin = (
        current_user.role is not None
        and current_user.role.name == settings.ADMIN_ROLE_NAME
    )
    is_allowed = user_id == current_user.id or is_admin

    if not is_allowed:
        raise ForbiddenException()

    if user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=user_id)
        if not user:
            raise BaseHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Usuário não encontrado.",
            )

    absences = crud.list_absences(
        session=session,
        user_id=user_id,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
    )
    return absences
