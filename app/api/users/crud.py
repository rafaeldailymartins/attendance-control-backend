from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, select

from app.api.app_config import crud as app_config_crud
from app.api.shifts import crud as shifts_crud
from app.api.shifts.schemas import ShiftCreate
from app.api.users.schemas import UserCreate, UserUpdate
from app.core.crud import db_update, paginate
from app.core.models import User
from app.core.security import get_password_hash, verify_password


def authenticate(session: Session, email: str, password: str):
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user


def list_users(session: Session, page: int | None = None, page_size: int | None = None):
    statement = select(User)
    return paginate(query=statement, session=session, page=page, page_size=page_size)


def get_user_by_id(session: Session, id: int):
    return session.get(User, id)


def get_user_by_email(session: Session, email: str | None):
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def create_user(session: Session, user_create: UserCreate):
    user = User.model_validate(
        user_create.model_dump(exclude={"shifts"}),
        update={"password": get_password_hash(user_create.password)},
    )
    session.add(user)
    session.flush()
    session.refresh(user)

    if user.id is None:
        raise ValueError("User ID is None. Cannot associate shifts without a user ID.")

    shifts = [
        ShiftCreate(**shift.model_dump(), user_id=user.id)
        for shift in user_create.shifts
    ]

    for shift in shifts:
        shifts_crud.create_shift(session, shift, commit=False)
    session.commit()
    return user


def update_user(session: Session, user: User, user_update: UserUpdate):
    app_config = app_config_crud.get_last_app_config(session)
    if not app_config:
        raise ValueError(
            "Ocorreu um erro no servidor e não foi possível encontrar as configurações."
        )

    user_data = user_update.model_dump(exclude_unset=True, exclude={"shifts"})

    if "password" in user_data:
        user_data["password"] = get_password_hash(user_data["password"])

    user_data["updated_shifts_at"] = datetime.now(ZoneInfo(app_config.zone_info))

    if user.id is None:
        raise ValueError("User ID is None. Cannot associate shifts without a user ID.")

    if user_update.shifts:
        shifts_crud.delete_shifts(session, user.shifts, commit=False)
        shifts = [
            ShiftCreate(**shift.model_dump(), user_id=user.id)
            for shift in user_update.shifts
        ]
        for shift in shifts:
            shifts_crud.create_shift(session, shift, commit=False, update_user=False)

    db_update(session, user, user_data)
    return user
