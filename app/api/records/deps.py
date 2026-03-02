from datetime import date
from typing import Annotated

from fastapi import Depends, Query

from app.api.records import crud
from app.api.records.schemas import AbsenceResponse
from app.api.users import crud as users_crud
from app.core.config import settings
from app.core.deps import CurrentUserDep, SessionDep
from app.core.exceptions import BadRequest, Forbidden, NotFound
from app.core.models import AttendanceType


def get_absences(
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
            raise NotFound("Usuário não encontrado.")

    if start_date > end_date:
        raise BadRequest("A data inicial deve ser menor ou igual a data final.")

    diff_days = (end_date - start_date).days

    if diff_days > 90:
        raise BadRequest("O período entre as datas deve ser menor que 90 dias.")

    absences = crud.list_absences(
        session=session,
        user_id=user_id,
        absence_type=absence_type,
        start_date=start_date,
        end_date=end_date,
    )
    return absences


GetAbsencesDep = Annotated[list[AbsenceResponse], Depends(get_absences)]
