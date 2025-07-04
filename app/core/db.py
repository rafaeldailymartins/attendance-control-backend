from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.crud import create_admin_role, create_first_admin, populate_app_config

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session):
    create_admin_role(session)
    create_first_admin(session=session)
    populate_app_config(session=session)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
