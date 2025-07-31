import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from app.api.app_config import crud as app_config_crud
from app.core.db import engine, init_db
from app.core.deps import get_current_user
from app.core.models import AppConfig, Attendance, DayOff, Role, Shift, User
from app.main import app
from app.tests.utils import CORRECT_LOGIN_DATA


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
        init_db(session)
        session.commit()


@pytest.fixture(scope="module")
def admin_token_headers(admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    return headers


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    response = client.post("/users/login", data=CORRECT_LOGIN_DATA)
    result = response.json()
    token = result["accessToken"]
    return token


@pytest.fixture(scope="module")
def admin_user(db: Session, admin_token: str):
    return get_current_user(db, admin_token)


@pytest.fixture(scope="session")
def app_config(db: Session):
    app_config = app_config_crud.get_last_app_config(db)
    if not app_config:
        raise ValueError(
            "Ocorreu um erro no servidor e não foi possível encontrar as configurações."
        )
    return app_config
