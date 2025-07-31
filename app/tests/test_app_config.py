from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api.app_config import crud
from app.api.app_config.schemas import AppConfigUpdate, DayOffCreate, RoleCreate
from app.core.config import settings
from app.core.models import DayOff, Role
from app.tests.utils import random_date, random_lower_string


def random_day_off_create():
    day_off_create = DayOffCreate(day=random_date(), description=random_lower_string())
    return day_off_create


def random_role_create():
    role_create = RoleCreate(name=random_lower_string())
    return role_create


def test_create_new_day_off(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    day_off_create = random_day_off_create()
    data = jsonable_encoder(day_off_create, exclude_unset=True)

    response = client.post("/config/days-off", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/config/days-off", json=data, headers=admin_token_headers)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert result["day"] == data["day"]
    assert result["description"] == data["description"]

    day_off_db = db.get(DayOff, result["id"])
    assert day_off_db
    assert day_off_db.day == day_off_create.day
    assert day_off_db.description == day_off_create.description


def test_create_new_role(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    role_create = random_role_create()
    data = jsonable_encoder(role_create, exclude_unset=True)

    response = client.post("/config/days-off", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/config/roles", json=data, headers=admin_token_headers)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert result["name"] == role_create.name

    role_db = db.get(Role, result["id"])
    assert role_db
    assert role_db.name == role_create.name


def test_update_role(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    role_create = random_role_create()
    role = crud.create_role(db, role_create)

    data = {"name": "updated_name"}

    response = client.patch(f"/config/roles/{role.id}", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(
        f"/config/roles/{role.id}",
        headers=admin_token_headers,
        json={"name": settings.ADMIN_ROLE_NAME},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.patch(
        f"/config/roles/{role.id}", headers=admin_token_headers, json=data
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["id"] == role.id
    assert result["name"] == data["name"]

    role_db = db.get(Role, role.id)
    db.refresh(role_db)
    assert role_db
    assert role_db.name == data["name"]


def test_update_app_config(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    last_app_config = crud.get_last_app_config(db)

    update = AppConfigUpdate(minutes_late=10)

    data = jsonable_encoder(update, exclude_unset=True)

    response = client.patch("/config", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch("/config", headers=admin_token_headers, json=data)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert result["minutesLate"] == update.minutes_late
    assert result["minutesEarly"] == last_app_config.minutes_early

    db.refresh(last_app_config)
    assert last_app_config.minutes_late == update.minutes_late


def test_delete_day_off(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    day_off_create = random_day_off_create()
    day_off = crud.create_day_off(db, day_off_create)

    response = client.delete(f"/config/days-off/{day_off.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(
        f"/config/days-off/{day_off.id}", headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK

    day_off_db = db.exec(select(DayOff).where(DayOff.id == day_off.id)).first()
    assert day_off_db is None


def test_delete_role(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    role_create = random_role_create()
    role = crud.create_role(db, role_create)

    response = client.delete(f"/config/roles/{role.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(f"/config/roles/{role.id}", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK

    role_db = db.exec(select(Role).where(Role.id == role.id)).first()
    assert role_db is None


def test_get_app_config(client: TestClient, admin_token_headers: dict[str, str]):
    response = client.get("/config", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert "minutesLate" in result
    assert "minutesEarly" in result


def test_get_days_off(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    day_off_create = random_day_off_create()
    crud.create_day_off(db, day_off_create)

    response = client.get("/config/days-off", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert "id" in item
        assert "day" in item
        assert "description" in item


def test_get_roles(client: TestClient, admin_token_headers: dict[str, str]):
    response = client.get("/config/roles", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert "id" in item
        assert "name" in item
