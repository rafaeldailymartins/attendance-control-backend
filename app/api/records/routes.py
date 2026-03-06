import csv
import io
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from app.api.records import crud
from app.api.records.deps import GetAbsencesDep
from app.api.records.schemas import (
    AbsenceCsvLine,
    AbsenceResponse,
    AttendanceCreate,
    AttendanceCsvLine,
    AttendanceResponse,
    AttendanceUpdate,
)
from app.api.shifts import crud as shifts_crud
from app.api.users import crud as users_crud
from app.core.config import settings
from app.core.crud import db_delete
from app.core.deps import CurrentUserDep, PaginationDep, SessionDep, check_admin
from app.core.exceptions import Forbidden, NotFound
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
        raise NotFound("Turno não encontrado.")

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
            raise NotFound("Turno não encontrado.")

    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise NotFound("Registro não encontrado.")
    crud.update_attendance(session, attendance, body)
    return attendance


@router.delete("/attendances/{attendance_id}", dependencies=[Depends(check_admin)])
def delete_attendance(session: SessionDep, attendance_id: int) -> Message:
    """
    Delete a attendance.
    """
    attendance = crud.get_attendance_by_id(session, attendance_id)
    if not attendance:
        raise NotFound("Registro não encontrado.")
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
            raise NotFound("Usuário não encontrado.")

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


@router.get("/absences")
def list_absences(absences: GetAbsencesDep) -> list[AbsenceResponse]:
    return absences


@router.post(
    "/absences/csv",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "CSV file",
        }
    },
)
def export_absences_to_csv(absences: GetAbsencesDep):
    data = [
        AbsenceCsvLine(
            user_name=absence.shift.user.name,
            day=absence.day,
            shift_start=absence.shift.start_time,
            shift_end=absence.shift.end_time,
            absence_type=absence.absence_type,
            minutes_late=absence.minutes_late,
            attendance_timestamp=absence.attendance_timestamp,
        ).model_dump(by_alias=True)
        for absence in absences
    ]

    fieldnames = list(data[0].keys()) if data else []

    buffer = io.StringIO()

    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=absences.csv"},
    )


@router.post(
    "/attendances/csv",
    response_class=StreamingResponse,
    responses={
        200: {
            "content": {"text/csv": {}},
            "description": "CSV file",
        }
    },
)
def export_attendances_to_csv(
    session: SessionDep,
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
    if user_id is not None:
        user = users_crud.get_user_by_id(session=session, id=user_id)
        if not user:
            raise NotFound("Usuário não encontrado.")

    attendances = crud.list_attendances(
        session=session,
        user_id=user_id,
        attendance_type=attendance_type,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )

    data = [
        AttendanceCsvLine(
            user_name=attendance.shift.user.name,
            weekday=attendance.shift.weekday,
            shift_start=attendance.shift.start_time,
            shift_end=attendance.shift.end_time,
            attendance_type=attendance.attendance_type,
            minutes_late=attendance.minutes_late,
            attendance_timestamp=attendance.timestamp,
        ).model_dump(by_alias=True)
        for attendance in attendances.items
    ]

    fieldnames = list(data[0].keys()) if data else []

    buffer = io.StringIO()

    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

    buffer.seek(0)

    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendances.csv"},
    )
