import random

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api.users import crud
from app.api.users.schemas import UserCreate, UserShiftCreate
from app.core.config import settings
from app.core.deps import get_current_user
from app.core.models import User, WeekdayEnum
from app.core.security import verify_password
from app.tests.test_shifts import assert_all_shift_fields
from app.tests.utils import (
    CORRECT_LOGIN_DATA,
    INCORRECT_LOGIN_DATA,
    random_email,
    random_lower_string,
    random_time,
)


def random_user_create(role_id: int | None = None):
    email = random_email()
    password = random_lower_string()
    name = random_lower_string()
    shifts = [
        UserShiftCreate(
            weekday=WeekdayEnum(random.randint(0, 6)),
            start_time=random_time(),
            end_time=random_time(),
        )
    ]
    user = UserCreate(
        email=email, name=name, password=password, shifts=shifts, role_id=role_id
    )
    return user


def assert_all_user_fields(
    user,
    id: int | None = None,
    email: str | None = None,
    name: str | None = None,
    role_id: int | None = None,
):
    assert "email" in user
    assert "name" in user
    assert "roleId" in user
    assert "shifts" in user
    assert "id" in user

    if id is not None:
        assert user["id"] == id
    if email is not None:
        assert user["email"] == email
    if name is not None:
        assert user["name"] == name
    if role_id is not None:
        assert user["roleId"] == role_id

    for shift in user["shifts"]:
        assert_all_shift_fields(shift)


def test_login(client: TestClient):
    response = client.post("/users/login", data=INCORRECT_LOGIN_DATA)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/users/login", data=CORRECT_LOGIN_DATA)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "accessToken" in result
    assert result["accessToken"]


def test_login_swagger(client: TestClient):
    response = client.post("/users/login/swagger", data=INCORRECT_LOGIN_DATA)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/users/login/swagger", data=CORRECT_LOGIN_DATA)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in result
    assert result["access_token"]


def test_get_me(client: TestClient, admin_token_headers: dict[str, str]):
    response = client.post("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/users/me", headers=admin_token_headers)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert_all_user_fields(result)


def test_create_user(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    user_create = random_user_create()

    response = client.post(
        "/users", json=jsonable_encoder(user_create, exclude_unset=True)
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post(
        "/users",
        json=jsonable_encoder(user_create, exclude_unset=True),
        headers=admin_token_headers,
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_all_user_fields(
        result,
        email=user_create.email,
        name=user_create.name,
        role_id=user_create.role_id,
    )

    user_db = db.get(User, result["id"])
    assert user_db
    assert user_db.email == user_create.email
    assert user_db.name == user_create.name
    assert user_db.role_id == user_create.role_id
    assert verify_password(user_create.password, user_db.password)


def test_get_users(client: TestClient, admin_token_headers: dict[str, str]):
    response = client.get("/users")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/users", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert_all_user_fields(item)


def test_get_user_by_id(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    user_create = random_user_create()
    user = crud.create_user(db, user_create)

    response = client.get(f"/users/{user.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(f"/users/{user.id}", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_all_user_fields(
        result, id=user.id, email=user.email, name=user.name, role_id=user.role_id
    )


def test_update_user(
    client: TestClient, db: Session, admin_token_headers: dict[str, str]
):
    user_create = random_user_create()
    user = crud.create_user(db, user_create)

    data = {"name": "updated_name", "password": "updated_password"}

    response = client.patch(f"/users/{user.id}", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(
        f"/users/{user.id}",
        headers=admin_token_headers,
        json={"email": settings.FIRST_ADMIN_EMAIL},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.patch(f"/users/{user.id}", headers=admin_token_headers, json=data)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert_all_user_fields(
        result, email=user.email, name=data["name"], role_id=user.role_id
    )

    user_db = db.get(User, user.id)
    db.refresh(user_db)
    assert user_db
    assert user_db.email == user.email
    assert user_db.name == data["name"]
    assert verify_password(data["password"], user_db.password)


def test_delete_user(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_token: str,
):
    user_create = random_user_create()
    user = crud.create_user(db, user_create)

    response = client.delete(f"/users/{user.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    current_user = get_current_user(db, admin_token)
    response = client.delete(f"/users/{current_user.id}", headers=admin_token_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    response = client.delete(f"/users/{user.id}", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK

    user_db = db.exec(select(User).where(User.id == user.id)).first()
    assert user_db is None
