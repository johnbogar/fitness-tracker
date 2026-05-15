import pytest
from datetime import date, timedelta
from app import app
from models.personal_record import PersonalRecord
from db import SessionLocal


# Use a high user_id unlikely to collide with real users
TEST_USER_ID = 99999


@pytest.fixture
def client():
    """Flask test client with testing config."""
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"
    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture(autouse=True)
def cleanup():
    """Ensure no leftover test records before/after each test."""
    _cleanup_records(TEST_USER_ID)
    yield
    _cleanup_records(TEST_USER_ID)


# ── Helpers ───────────────────────────────────────────────────────────────────
def _cleanup_records(user_id):
    db = SessionLocal()
    try:
        db.query(PersonalRecord).filter(
            PersonalRecord.user_id == user_id
        ).delete()
        db.commit()
    finally:
        db.close()


def _create_test_record(
    user_id=TEST_USER_ID,
    exercise="Bench Press",
    value=225.0,
    unit="lbs",
    achieved_on=None,
    notes="Test PR",
):
    """Insert a personal record directly into the DB."""
    db = SessionLocal()
    try:
        pr = PersonalRecord(
            user_id=user_id,
            exercise=exercise,
            value=value,
            unit=unit,
            achieved_on=achieved_on or date.today(),
            notes=notes,
        )
        db.add(pr)
        db.commit()
        db.refresh(pr)
        return pr
    finally:
        db.close()


def _login(client, user_id=TEST_USER_ID):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


# ── GET /api/personal_records ─────────────────────────────────────────────────

def test_get_personal_records_unauthorized(client):
    """Anonymous request returns 401."""
    response = client.get("/api/personal_records")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Not logged in"


def test_get_personal_records_empty(client):
    """Logged-in user with no records gets an empty list."""
    _login(client)
    response = client.get("/api/personal_records")
    assert response.status_code == 200
    assert response.get_json() == []


def test_get_personal_records_returns_user_records(client):
    """Logged-in user receives their own records."""
    _login(client)
    pr = _create_test_record(exercise="Squat", value=315.0, unit="lbs")
    response = client.get("/api/personal_records")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    record = data[0]
    assert record["id"] == pr.id
    assert record["exercise"] == "Squat"
    assert record["value"] == 315.0
    assert record["unit"] == "lbs"
    assert record["achieved_on"] == date.today().isoformat()


def test_get_personal_records_orders_by_date_desc(client):
    """Records are returned newest first by achieved_on."""
    _login(client)
    older = _create_test_record(
        exercise="Deadlift",
        value=405.0,
        achieved_on=date.today() - timedelta(days=5),
    )
    newer = _create_test_record(
        exercise="Deadlift",
        value=415.0,
        achieved_on=date.today() - timedelta(days=1),
    )
    response = client.get("/api/personal_records")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["id"] == newer.id
    assert data[1]["id"] == older.id


def test_get_personal_records_isolated_per_user(client):
    """A user only sees their own records."""
    _login(client)
    _create_test_record(user_id=TEST_USER_ID, exercise="Mine")
    other_user_id = TEST_USER_ID + 1
    try:
        _create_test_record(user_id=other_user_id, exercise="Theirs")
        response = client.get("/api/personal_records")
        assert response.status_code == 200
        data = response.get_json()
        assert all(r["exercise"] == "Mine" for r in data)
    finally:
        _cleanup_records(other_user_id)


# ── POST /api/personal_records ────────────────────────────────────────────────

def test_add_personal_record_unauthorized(client):
    """Anonymous POST returns 401."""
    response = client.post("/api/personal_records", json={
        "exercise": "Bench", "value": 200
    })
    assert response.status_code == 401


def test_add_personal_record_success(client):
    """Logged-in user can create a personal record."""
    _login(client)
    payload = {
        "exercise": "Overhead Press",
        "value": 135,
        "unit": "lbs",
        "achieved_on": "2026-04-15",
        "notes": "Felt strong",
    }
    response = client.post("/api/personal_records", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["exercise"] == "Overhead Press"
    assert data["value"] == 135.0
    assert data["unit"] == "lbs"
    assert data["achieved_on"] == "2026-04-15"
    assert data["notes"] == "Felt strong"
    assert "id" in data


def test_add_personal_record_defaults_achieved_on_to_today(client):
    """When achieved_on is omitted, today's date is used."""
    _login(client)
    response = client.post("/api/personal_records", json={
        "exercise": "Pull-up",
        "value": 10,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["achieved_on"] == date.today().isoformat()


def test_add_personal_record_strips_exercise_whitespace(client):
    """Leading/trailing whitespace in exercise is stripped."""
    _login(client)
    response = client.post("/api/personal_records", json={
        "exercise": "   Row   ",
        "value": 185,
    })
    assert response.status_code == 201
    assert response.get_json()["exercise"] == "Row"


def test_add_personal_record_missing_exercise(client):
    """Missing exercise returns 400."""
    _login(client)
    response = client.post("/api/personal_records", json={"value": 100})
    assert response.status_code == 400
    assert "exercise" in response.get_json()["error"].lower()


def test_add_personal_record_blank_exercise(client):
    """Blank/whitespace-only exercise returns 400."""
    _login(client)
    response = client.post("/api/personal_records", json={
        "exercise": "   ",
        "value": 100,
    })
    assert response.status_code == 400


def test_add_personal_record_missing_value(client):
    """Missing value returns 400."""
    _login(client)
    response = client.post("/api/personal_records", json={"exercise": "Squat"})
    assert response.status_code == 400


def test_add_personal_record_invalid_value(client):
    """Non-numeric value returns 400."""
    _login(client)
    response = client.post("/api/personal_records", json={
        "exercise": "Squat",
        "value": "not-a-number",
    })
    assert response.status_code == 400
    assert "number" in response.get_json()["error"].lower()


def test_add_personal_record_persists_to_db(client):
    """New record is actually saved in the database."""
    _login(client)
    response = client.post("/api/personal_records", json={
        "exercise": "Clean",
        "value": 175.5,
        "unit": "lbs",
    })
    assert response.status_code == 201
    record_id = response.get_json()["id"]

    db = SessionLocal()
    try:
        pr = db.query(PersonalRecord).filter(
            PersonalRecord.id == record_id
        ).first()
        assert pr is not None
        assert pr.exercise == "Clean"
        assert float(pr.value) == 175.5
    finally:
        db.close()


# ── DELETE /api/personal_records/<id> ─────────────────────────────────────────

def test_delete_personal_record_unauthorized(client):
    """Anonymous DELETE returns 401."""
    response = client.delete("/api/personal_records/1")
    assert response.status_code == 401


def test_delete_personal_record_success(client):
    """Owner can delete their own record."""
    _login(client)
    pr = _create_test_record()
    response = client.delete(f"/api/personal_records/{pr.id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Deleted"

    db = SessionLocal()
    try:
        assert db.query(PersonalRecord).filter(
            PersonalRecord.id == pr.id
        ).first() is None
    finally:
        db.close()


def test_delete_personal_record_not_found(client):
    """Deleting a non-existent record returns 404."""
    _login(client)
    response = client.delete("/api/personal_records/99999999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Record not found"


def test_delete_personal_record_other_user_forbidden(client):
    """A user cannot delete another user's record (returns 404)."""
    other_user_id = TEST_USER_ID + 1
    pr = _create_test_record(user_id=other_user_id)
    try:
        _login(client)  # login as TEST_USER_ID
        response = client.delete(f"/api/personal_records/{pr.id}")
        assert response.status_code == 404

        # Confirm the record still exists
        db = SessionLocal()
        try:
            assert db.query(PersonalRecord).filter(
                PersonalRecord.id == pr.id
            ).first() is not None
        finally:
            db.close()
    finally:
        _cleanup_records(other_user_id)
