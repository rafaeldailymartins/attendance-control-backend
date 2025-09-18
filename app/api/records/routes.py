from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.records import crud
from app.api.records.schemas import (
    AbsenceResponse,
    AttendanceCreate,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.api.shifts import crud as shifts_crud
from app.api.users import crud as users_crud
from app.core.config import settings
from app.core.crud import db_delete
from app.core.deps import CurrentUserDep, PaginationDep, SessionDep, check_admin
from app.core.exceptions import (
    AttendanceNotFound,
    Forbidden,
    ShiftNotFound,
    UserNotFound,
)
from app.core.models import AttendanceType
from app.core.schemas import Message, Page

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/attendances", response_model=AttendanceResponse)
def create_new_attendance(
    session: SessionDep, body: AttendanceCreate, current_user: CurrentUserDep
):
    """
    Create new attendance (Clock in or Clock out)
    """
    shift = shifts_crud.get_shift_by_id(session, body.shift_id)
    if not shift:
        raise ShiftNotFound()

    is_admin = (
        current_user.role is not None
        and current_user.role.name == settings.ADMIN_ROLE_NAME
    )
    is_allowed = shift.user_id == current_user.id or is_admin

    if not is_allowed:
        raise Forbidden()

    attendance = crud.create_attendance(
        session=session, shift=shift, attendance_type=body.attendance_type
    )
    return attendance


@router.patch(
    "/attendances/{attendance_id}",
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
            raise ShiftNotFound()

    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise AttendanceNotFound()
    crud.update_attendance(session, attendance, body)
    return attendance


@router.delete("/attendances/{attendance_id}", dependencies=[Depends(check_admin)])
def delete_attendance(session: SessionDep, attendance_id: int) -> Message:
    """
    Delete a attendance.
    """
    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise AttendanceNotFound()
    db_delete(session, attendance)
    return Message(message="Registro deletado com sucesso")


@router.get("/attendances", response_model=Page[AttendanceResponse])
def list_attendances(
    session: SessionDep,
    pagination: PaginationDep,
    user_id: Annotated[int | None, Query(description="Filter by user id.")] = None,
    attendance_type: Annotated[
        AttendanceType | None,
        Query(
            description="Filter by attendance type. "
            "It can be 0 for clock in, or 1 for clock out."
        ),
    ] = None,
    start_timestamp: Annotated[
        datetime | None, Query(description="Filter by a start datetime")
    ] = None,
    end_timestamp: Annotated[
        datetime | None, Query(description="Filter by a end datetime")
    ] = None,
):
    """
    List attendances.
    Attendances of inactive users will not be shown.
    """
    if user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=user_id)
        if not user:
            raise UserNotFound()

    attendances = crud.list_attendances(
        session=session,
        user_id=user_id,
        attendance_type=attendance_type,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        page=pagination.page,
        page_size=pagination.page_size,
    )
    return attendances


@router.get(
    "/absences",
    response_model=list[AbsenceResponse],
)
def list_absences(
    session: SessionDep,
    current_user: CurrentUserDep,
    start_date: Annotated[
        date,
        Query(description="The initial date that will be used to search for absences"),
    ],
    end_date: Annotated[
        date,
        Query(description="The final date that will be used to search for absences"),
    ],
    user_id: Annotated[int | None, Query(description="Filter by user id.")] = None,
    absence_type: Annotated[
        AttendanceType | None,
        Query(
            description="Filter by absence type. "
            "It can be 0 for clock in, or 1 for clock out."
        ),
    ] = None,
):
    """
    Returns absences between two dates.
    Absences of inactive users or days off will not be shown.
    """

    is_admin = (
        current_user.role is not None
        and current_user.role.name == settings.ADMIN_ROLE_NAME
    )
    is_allowed = user_id == current_user.id or is_admin

    if not is_allowed:
        raise Forbidden()

    if user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=user_id)
        if not user:
            raise UserNotFound()

    absences = crud.list_absences(
        session=session,
        user_id=user_id,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
    )
    return absences
