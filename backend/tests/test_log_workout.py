import pytest
from app import app
from models.workout import Workout
from db import SessionLocal


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"
    with app.test_client() as client:
        yield client


# ── Helper ────────────────────────────────────────────────────────────────────

def create_test_workout(user_id=1, goal_id=None, date_str="2026-04-01", notes="Test notes"):
    """Insert a workout directly into the DB and return its ORM object."""
    from datetime import datetime
    db = SessionLocal()
    workout = Workout(
        user_id=user_id,
        goal_id=goal_id,
        date=datetime.strptime(date_str, "%Y-%m-%d").date(),
        notes=notes,
    )
    db.add(workout)
    db.commit()
    db.refresh(workout)
    db.close()
    return workout


# ── POST /api/log_workout ─────────────────────────────────────────────────────

def test_log_workout_success(client):
    """Normal case: logged-in user submits a valid workout log."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "goalId": None,
        "date": "2026-04-01",
        "notes": "Morning run"
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert "id" in data
    assert data["user_id"] == 1
    assert data["goal_id"] is None
    assert data["date"] == "2026-04-01"
    assert data["notes"] == "Morning run"
    assert "created_at" in data


def test_log_workout_with_goal_id(client):
    """Normal case: workout associated with a specific goal."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "goalId": 1,
        "date": "2026-04-02",
        "notes": "Leg day"
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["goal_id"] == 1


def test_log_workout_no_date_defaults_to_today(client):
    """Omitting date should default to today without error."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {"notes": "No date provided"}
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    from datetime import date
    assert data["date"] == str(date.today())


def test_log_workout_unauthorized(client):
    """Unauthenticated POST to /api/log_workout must return 401."""
    payload = {
        "goalId": None,
        "date": "2026-04-01",
        "notes": "Should not be logged"
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 401

    data = response.get_json()
    assert "error" in data


def test_log_workout_invalid_date_format(client):
    """Invalid date format (MM-DD-YYYY) should return 400."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "date": "04-13-2026",   # wrong format
        "notes": "Bad date"
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data
    assert "YYYY-MM-DD" in data["error"]


def test_log_workout_non_int_goal_id(client):
    """Non-integer goalId should return 400."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "goalId": "not-an-int",
        "date": "2026-04-01",
        "notes": "Bad goal id"
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data


def test_log_workout_notes_too_long(client):
    """Notes exceeding 1000 characters should return 400."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "date": "2026-04-01",
        "notes": "x" * 1001
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data


def test_log_workout_notes_not_string(client):
    """Non-string notes value should return 400."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "date": "2026-04-01",
        "notes": 12345
    }
    response = client.post("/api/log_workout", json=payload)
    assert response.status_code == 400


def test_log_workout_no_json_body(client):
    """Sending no JSON body should return 400 without crashing."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post("/api/log_workout", data="not json",
                           content_type="text/plain")
    assert response.status_code in (400, 415)


def test_log_workout_no_crash_on_empty_json(client):
    """Empty JSON object should not crash the server."""
    with client.session_transaction() as sess:
        sess["user_id"] = 1


    response = client.post("/api/log_workout", json={})
            # Server should not crash — may return 201 or
    assert response is not None
    # Empty JSON is valid — date defaults to today, notes default to ""
    assert response.status_code in (201, 400)


# ── GET /api/workouts ─────────────────────────────────────────────────────────

def test_get_workouts_success(client):
    """Logged-in user can retrieve their workout list."""
    workout = create_test_workout(user_id=2, date_str="2026-03-10", notes="Swim")

    with client.session_transaction() as sess:
        sess["user_id"] = 2

    response = client.get("/api/workouts")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert any(w["id"] == workout.id for w in data)


def test_get_workouts_unauthorized(client):
    """Unauthenticated GET /api/workouts must return 401."""
    response = client.get("/api/workouts")
    assert response.status_code == 401


def test_get_workouts_only_own_workouts(client):
    """User should only see their own workouts, not other users'."""
    # create a workout for user 10
    create_test_workout(user_id=10, notes="User 10 workout")

    with client.session_transaction() as sess:
        sess["user_id"] = 99   # different user

    response = client.get("/api/workouts")
    assert response.status_code == 200

    data = response.get_json()
    for w in data:
        # all returned workouts must belong to user 99
        # (we verify via the workout IDs we know belong to user 10)
        assert w.get("notes") != "User 10 workout"


def test_get_workouts_returns_list(client):
    """Response should always be a JSON array (even when empty)."""
    with client.session_transaction() as sess:
        sess["user_id"] = 999  # user with no workouts

    response = client.get("/api/workouts")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)