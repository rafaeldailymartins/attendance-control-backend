from fastapi import APIRouter, Depends, status

from app.api.app_config import crud
from app.api.app_config.schemas import (
    AppConfigResponse,
    AppConfigUpdate,
    DayOffCreate,
    DayOffResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
)
from app.core.crud import db_delete
from app.core.deps import SessionDep, check_admin, get_current_user
from app.core.exceptions import BaseHTTPException
from app.core.schemas import Message

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
    role = crud.get_role_by_name(session, body.name)
    if role:
        raise BaseHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            message="Já existe um cargo com este nome no sistema.",
        )

    role_create = RoleCreate.model_validate(body)
    role = crud.create_role(session, role_create)
    return role


@router.patch(
    "/roles/{role_id}", response_model=RoleResponse, dependencies=[Depends(check_admin)]
)
def update_role(session: SessionDep, role_id: int, body: RoleUpdate):
    """
    Update a role
    """
    if body.name:
        role = crud.get_role_by_name(session=session, name=body.name)
        if role and role.id != role_id:
            raise BaseHTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Já existe um cargo com este nome no sistema.",
            )

    role = crud.get_role_by_id(session, role_id)
    if not role:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Cargo não encontrado"
        )
    crud.update_role(session, role, body)
    return role


@router.patch(
    "/", response_model=AppConfigResponse, dependencies=[Depends(check_admin)]
)
def update_app_config(session: SessionDep, body: AppConfigUpdate):
    """
    Update settings
    """

    app_config = crud.get_last_app_config(session)
    if not app_config:
        raise BaseHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Ocorreu um erro no servidor e "
            "não foi possível encontrar as configurações.",
        )
    crud.update_app_config(session, app_config, body)
    return app_config


@router.delete("/days-off/{day_off_id}", dependencies=[Depends(check_admin)])
def delete_day_off(session: SessionDep, day_off_id: int) -> Message:
    """
    Delete a day off.
    """
    day_off = crud.get_day_off_by_id(session, day_off_id)
    if not day_off:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Dia livre não encontrado"
        )
    db_delete(session, day_off)
    return Message(message="Dia livre deletado com sucesso")


@router.delete("/roles/{role_id}", dependencies=[Depends(check_admin)])
def delete_role(session: SessionDep, role_id: int) -> Message:
    """
    Delete a role.
    """
    role = crud.get_role_by_id(session, role_id)
    if not role:
        raise BaseHTTPException(
            status_code=status.HTTP_404_NOT_FOUND, message="Cargo não encontrado"
        )
    db_delete(session, role)
    return Message(message="Cargo deletado com sucesso")


@router.get(
    "/", response_model=AppConfigResponse, dependencies=[Depends(get_current_user)]
)
def get_app_config(session: SessionDep):
    """
    Get settings
    """
    app_config = crud.get_last_app_config(session)
    if not app_config:
        raise BaseHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Ocorreu um erro no servidor e "
            "não foi possível encontrar as configurações.",
        )
    return app_config


@router.get(
    "/days-off",
    response_model=list[DayOffResponse],
    dependencies=[Depends(get_current_user)],
)
def list_days_off(session: SessionDep):
    """
    Get all days off
    """
    days_off = crud.list_days_off(session)
    return days_off
