from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlmodel import Session, delete, select

from app.api.attendances import crud
from app.api.attendances.schemas import AttendanceCreate
from app.api.shifts import crud as shifts_crud
from app.core.models import AppConfig, Attendance, AttendanceType, User
from app.tests.test_shifts import new_shift_create


def test_create_new_attendance(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shift = shifts_crud.create_shift(db, shift_create)

    attendance_create = AttendanceCreate(
        attendance_type=AttendanceType.CLOCK_IN, shift_id=shift.id
    )
    data = jsonable_encoder(attendance_create, exclude_unset=True)

    response = client.post("/attendances", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.post("/attendances", json=data, headers=admin_token_headers)
    result = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert "timestamp" in result
    assert result["attendanceType"] == data["attendanceType"]
    assert result["shiftId"] == data["shiftId"]
    assert result["minutesLate"] == 0

    attendance_db = db.get(Attendance, result["id"])
    assert attendance_db
    assert attendance_db.attendance_type == attendance_create.attendance_type
    assert attendance_db.shift_id == attendance_create.shift_id
    assert attendance_db.minutes_late == result["minutesLate"]
    assert attendance_db.timestamp == datetime.fromisoformat(result["timestamp"])


def test_update_attendance(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shift = shifts_crud.create_shift(db, shift_create)

    attendance = crud.create_attendance(db, shift, AttendanceType.CLOCK_IN)

    data = {"attendanceType": AttendanceType.CLOCK_OUT}

    response = client.patch(f"/attendances/{attendance.id}", json=data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.patch(
        f"/attendances/{attendance.id}", headers=admin_token_headers, json=data
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert "id" in result
    assert result["timestamp"] == attendance.timestamp.isoformat()
    assert result["attendanceType"] == data["attendanceType"]
    assert result["shiftId"] == attendance.shift_id
    assert result["minutesLate"] == attendance.minutes_late

    attendance_db = db.get(Attendance, attendance.id)
    db.refresh(attendance_db)
    assert attendance_db
    assert attendance_db.attendance_type == data["attendanceType"]
    assert attendance_db.shift_id == attendance.shift_id
    assert attendance_db.minutes_late == attendance.minutes_late
    assert attendance_db.timestamp == attendance.timestamp


def test_delete_attendance(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shift = shifts_crud.create_shift(db, shift_create)

    attendance = crud.create_attendance(db, shift, AttendanceType.CLOCK_IN)

    response = client.delete(f"/attendances/{attendance.id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.delete(
        f"/attendances/{attendance.id}", headers=admin_token_headers
    )
    assert response.status_code == status.HTTP_200_OK

    attendance_db = db.exec(
        select(Attendance).where(Attendance.id == attendance.id)
    ).first()
    assert attendance_db is None


def test_get_attendances(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shift = shifts_crud.create_shift(db, shift_create)

    crud.create_attendance(db, shift, AttendanceType.CLOCK_IN)

    response = client.get("/attendances", headers=admin_token_headers)
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert "id" in item
        assert "attendanceType" in item
        assert "shiftId" in item
        assert "timestamp" in item
        assert "minutesLate" in item


def test_get_absences(
    client: TestClient,
    db: Session,
    admin_token_headers: dict[str, str],
    admin_user: User,
    app_config: AppConfig,
):
    assert admin_user.id is not None

    shift_create = new_shift_create(
        admin_user.id, datetime.now(ZoneInfo(app_config.zone_info))
    )
    shifts_crud.create_shift(db, shift_create)

    db.exec(delete(Attendance))  # type: ignore
    db.commit()

    today = datetime.now(ZoneInfo(app_config.zone_info)).date().isoformat()
    params = {
        "start_date": today,
        "end_date": today,
    }

    response = client.get("/attendances/absences")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get(
        "/attendances/absences", headers=admin_token_headers, params=params
    )
    result = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(result) > 0
    for item in result:
        assert "shiftId" in item
        assert "day" in item
        assert "absenceType" in item
        assert "minutesLate" in item
        assert "attendanceTimestamp" in item
