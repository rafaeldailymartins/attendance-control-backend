from fastapi import APIRouter, status

from app.api.attendances import crud
from app.api.attendances.schemas import AttendanceCreate, AttendanceResponse
from app.api.shifts import crud as shifts_crud
from app.core.config import settings
from app.core.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BaseHTTPException, ForbiddenException

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
