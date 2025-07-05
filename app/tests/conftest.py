import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.core.db import engine, init_db
from app.core.models import AppConfig, Attendance, DayOff, Role, Shift, User
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def db():
    with Session(engine) as session:
        init_db(session)
        yield session
        session.exec(delete(Attendance))  # type: ignore
        session.exec(delete(Shift))  # type: ignore
        session.exec(delete(User))  # type: ignore
        session.exec(delete(Role))  # type: ignore
        session.exec(delete(DayOff))  # type: ignore
        session.exec(delete(AppConfig))  # type: ignore
        session.commit()
