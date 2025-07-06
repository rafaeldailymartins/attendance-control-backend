from fastapi import APIRouter, Depends

from app.api.app_config import crud
from app.api.app_config.schemas import (
    DayOffCreate,
    DayOffResponse,
    RoleCreate,
    RoleResponse,
)
from app.core.deps import SessionDep, check_admin

router = APIRouter(prefix="/config", tags=["config"])


@router.post(
    "/days-off", response_model=DayOffResponse, dependencies=[Depends(check_admin)]
)
def create_new_day_off(session: SessionDep, body: DayOffCreate):
    """
    Create new day off
    """
    day_off_create = DayOffCreate.model_validate(body)
    day_off = crud.create_day_off(session, day_off_create)
    return day_off


@router.post("/roles", response_model=RoleResponse, dependencies=[Depends(check_admin)])
def create_new_role(session: SessionDep, body: RoleCreate):
    """
    Create new role
    """
    role_create = RoleCreate.model_validate(body)
    role = crud.create_role(session, role_create)
    return role
