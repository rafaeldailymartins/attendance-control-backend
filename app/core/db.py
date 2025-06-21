from sqlmodel import SQLModel, create_engine, Session
from typing import Annotated
from fastapi import Depends
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from app.core.crud import create_admin_role, create_first_admin, reset_app_config
from app.core.config import settings

connect_args = {
    "check_same_thread": False
}  # TODO: Remove this when switching from SQLite to another database
engine = create_engine(str(settings.DATABASE_URL), connect_args=connect_args)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(
    dbapi_connection, connection_record
):  # TODO: Remove this when switching from SQLite to another database
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def init_db():
    SQLModel.metadata.create_all(engine)

    session = next(get_session())
    create_admin_role(session)
    create_first_admin(session=session)
    reset_app_config(session=session)
    


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
