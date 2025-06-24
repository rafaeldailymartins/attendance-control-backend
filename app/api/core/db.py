from sqlmodel import create_engine, Session
from typing import Annotated
from fastapi import Depends
from app.api.core.crud import create_admin_role, create_first_admin, reset_app_config
from app.api.core.config import settings

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db():
    session = next(get_session())
    create_admin_role(session)
    create_first_admin(session=session)
    reset_app_config(session=session)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
