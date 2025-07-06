from fastapi import APIRouter, Depends

from app.api.app_config import crud
from app.api.app_config.schemas import DayOffCreate, DayOffResponse
from app.core.deps import SessionDep, check_admin

router = APIRouter(prefix="/config", tags=["config"])


@router.post(
    "/days-off", response_model=DayOffResponse, dependencies=[Depends(check_admin)]
)
def create_new_user(session: SessionDep, body: DayOffCreate):
    """
    Create new day off
    """
    day_off_create = DayOffCreate.model_validate(body)
    user = crud.create_day_off(session, day_off_create)
    return user
