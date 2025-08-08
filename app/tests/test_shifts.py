import random
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.api.shifts import crud
from app.api.shifts.schemas import ShiftCreate
from app.core.models import AppConfig, Shift, User, WeekdayEnum
from app.tests.utils import random_time


def random_shift_create(user_id: int):
    shift_create = ShiftCreate(
        weekday=WeekdayEnum(random.randint(0, 6)),
        start_time=random_time(),
        end_time=random_time(),
        user_id=user_id,
    )
    return shift_create


def new_shift_create(user_id: int, start_datetime: datetime):
    end_datetime = start_datetime + timedelta(hours=1)

    start_time = start_datetime.time().replace(microsecond=0)
    end_time = end_datetime.time().replace(microsecond=0)

    if end_datetime.date() > start_datetime.date():
        end_time = time(23, 59, 59)

    shift_create = ShiftCreate(
        weekday=WeekdayEnum(start_datetime.weekday()),
        start_time=start_time,
        end_time=end_time,
        user_id=user_id,
    )
    return shift_create


def test_create_new_shift(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
):
    assert admin_user.id is not None

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
    admin_user: User,
):
    assert admin_user.id is not None

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
    admin_user: User,
):
    assert admin_user.id is not None

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
    admin_user: User,
):
    assert admin_user.id is not None

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


def test_get_current_shift(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    crud.delete_shifts(db, admin_user.shifts)

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shift = jsonable_encoder(crud.create_shift(db, shift_create))

    response = client.get(
        "/shifts/current",
        params={"user_id": admin_user.id, "attendance_type": random.randint(0, 1)},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        "/shifts/current",
        headers=admin_token_headers,
        params={"user_id": admin_user.id, "attendance_type": random.randint(0, 1)},
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK

    assert result["message"] == "OK"
    assert result["shift"]
    shift_result = result["shift"]
    assert shift_result["id"] == shift["id"]
    assert shift_result["weekday"] == shift["weekday"]
    assert shift_result["startTime"] == shift["start_time"]
    assert shift_result["endTime"] == shift["end_time"]
    assert shift_result["userId"] == shift["user_id"]
