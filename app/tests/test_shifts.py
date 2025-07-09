import random

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api.shifts import crud
from app.api.shifts.schemas import ShiftCreate
from app.api.users.schemas import UserResponse
from app.core.models import Shift, WeekdayEnum
from app.tests.utils import random_time


def random_shift_create(user_id: int):
    shift_create = ShiftCreate(
        weekday=WeekdayEnum(random.randint(0, 6)),
        start_time=random_time(),
        end_time=random_time(),
        user_id=user_id,
    )
    return shift_create


def test_create_new_shift(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: UserResponse,
):
    shift_create = random_shift_create(admin_user.id)
    data = jsonable_encoder(shift_create, exclude_unset=True)

    response = client.post("/shifts", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/shifts", json=data, headers=admin_token_headers)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert result["weekday"] == data["weekday"]
    assert result["startTime"] == data["startTime"]
    assert result["endTime"] == data["endTime"]
    assert result["userId"] == data["userId"]

    shift_db = db.get(Shift, result["id"])
    assert shift_db
    assert shift_db.weekday == shift_create.weekday
    assert shift_db.start_time == shift_create.start_time
    assert shift_db.end_time == shift_create.end_time
    assert shift_db.user_id == shift_create.user_id


def test_update_shift(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: UserResponse,
):
    shift_create = random_shift_create(admin_user.id)
    shift = crud.create_shift(db, shift_create)

    new_start_time = random_time()
    data = {"startTime": new_start_time.strftime("%H:%M:%S")}

    response = client.patch(f"/shifts/{shift.id}", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(
        f"/shifts/{shift.id}", headers=admin_token_headers, json=data
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert result["weekday"] == shift.weekday
    assert result["startTime"] == data["startTime"]
    assert result["userId"] == shift.user_id

    shift_db = db.get(Shift, shift.id)
    db.refresh(shift_db)
    assert shift_db
    assert shift_db.weekday == shift_create.weekday
    assert shift_db.start_time == new_start_time
    assert shift_db.end_time == shift_create.end_time
    assert shift_db.user_id == shift_create.user_id


def test_delete_shift(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: UserResponse,
):
    shift_create = random_shift_create(admin_user.id)
    shift = crud.create_shift(db, shift_create)

    response = client.delete(f"/shifts/{shift.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(f"/shifts/{shift.id}", headers=admin_token_headers)
    assert response.status_code == status.HTTP_200_OK

    shift_db = db.exec(select(Shift).where(Shift.id == shift.id)).first()
    assert shift_db is None


def test_get_shifts(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: UserResponse,
):
    shift_create = random_shift_create(admin_user.id)
    crud.create_shift(db, shift_create)

    response = client.get("/shifts")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/shifts", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert "id" in item
        assert "weekday" in item
        assert "startTime" in item
        assert "endTime" in item
        assert "userId" in item
