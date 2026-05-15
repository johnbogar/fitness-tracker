import pytest
from datetime import date, timedelta
from app import app
from models.workout import Workout
from db import SessionLocal


# Use a high user_id unlikely to collide with real users
TEST_USER_ID = 88888


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
    """Ensure no leftover workouts before/after each test."""
    _cleanup_workouts(TEST_USER_ID)
    yield
    _cleanup_workouts(TEST_USER_ID)


# ── Helpers ────────────────────────────────────────
def _cleanup_workouts(user_id):
    db = SessionLocal()
    try:
        db.query(Workout).filter(Workout.user_id == user_id).delete()
        db.commit()
    finally:
        db.close()


def _add_workout(user_id, workout_date, notes="test"):
    db = SessionLocal()
    try:
        w = Workout(user_id=user_id, date=workout_date, notes=notes)
        db.add(w)
        db.commit()
        db.refresh(w)
        return w
    finally:
        db.close()


def _login(client, user_id=TEST_USER_ID):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


# ── GET /api/streak ─────────────────────────────────────

def test_get_streak_unauthorized(client):
    """Anonymous request returns 401."""
    response = client.get("/api/streak")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Unauthorized"


def test_get_streak_no_workouts(client):
    """User with no workouts has zero streak values."""
    _login(client)
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"currentStreak": 0, "longestStreak": 0}


def test_get_streak_single_workout_today(client):
    """A single workout today gives current=1, longest=1."""
    _login(client)
    _add_workout(TEST_USER_ID, date.today())
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 1
    assert data["longestStreak"] == 1


def test_get_streak_single_workout_yesterday(client):
    """A single workout yesterday still counts as current streak of 1."""
    _login(client)
    _add_workout(TEST_USER_ID, date.today() - timedelta(days=1))
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 1
    assert data["longestStreak"] == 1


def test_get_streak_old_workout_breaks_current(client):
    """A workout from days ago does not contribute to current streak."""
    _login(client)
    _add_workout(TEST_USER_ID, date.today() - timedelta(days=5))
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 0
    assert data["longestStreak"] == 1


def test_get_streak_consecutive_days(client):
    """Three consecutive days ending today => current=3, longest=3."""
    _login(client)
    today = date.today()
    _add_workout(TEST_USER_ID, today - timedelta(days=2))
    _add_workout(TEST_USER_ID, today - timedelta(days=1))
    _add_workout(TEST_USER_ID, today)
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 3
    assert data["longestStreak"] == 3


def test_get_streak_duplicate_dates_count_once(client):
    """Multiple workouts on the same day count as one streak day."""
    _login(client)
    today = date.today()
    _add_workout(TEST_USER_ID, today, notes="morning")
    _add_workout(TEST_USER_ID, today, notes="evening")
    _add_workout(TEST_USER_ID, today - timedelta(days=1))
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 2
    assert data["longestStreak"] == 2


def test_get_streak_broken_streak(client):
    """
    Longest streak must reflect a previous broken streak.
    Pattern: days 10-7 ago (4 in a row), then today only.
    Expected: longest=4, current=1.
    """
    _login(client)
    today = date.today()
    for offset in (10, 9, 8, 7):
        _add_workout(TEST_USER_ID, today - timedelta(days=offset))
    _add_workout(TEST_USER_ID, today)
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 1
    assert data["longestStreak"] == 4


def test_get_streak_current_equals_longest_when_active(client):
    """When the current run is the longest run, both equal each other."""
    _login(client)
    today = date.today()
    # past broken streak of length 2
    _add_workout(TEST_USER_ID, today - timedelta(days=15))
    _add_workout(TEST_USER_ID, today - timedelta(days=14))
    # current streak of length 4
    for offset in (3, 2, 1, 0):
        _add_workout(TEST_USER_ID, today - timedelta(days=offset))
    response = client.get("/api/streak")
    assert response.status_code == 200
    data = response.get_json()
    assert data["currentStreak"] == 4
    assert data["longestStreak"] == 4


def test_get_streak_isolated_per_user(client):
    """Other users' workouts do not influence this user's streak."""
    other_user_id = TEST_USER_ID + 1
    today = date.today()
    try:
        # populate other user with a long streak
        for offset in range(10):
            _add_workout(other_user_id, today - timedelta(days=offset))
        # current user only has today
        _login(client)
        _add_workout(TEST_USER_ID, today)
        response = client.get("/api/streak")
        assert response.status_code == 200
        data = response.get_json()
        assert data["currentStreak"] == 1
        assert data["longestStreak"] == 1
    finally:
        _cleanup_workouts(other_user_id)
