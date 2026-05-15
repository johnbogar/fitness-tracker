import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_add_goal_success(client):
    """
    Test successful goal creation
    """
    payload = {
        "goalName": "Learn Flask",
        "goalDesc": "Build an API",
        "userId": 1,
        "endDate": "2026-05-01"
    }
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.post("/api/add_goal", json=payload)

    assert response.status_code == 201

    data = response.get_json()

    assert "id" in data
    assert data["goalname"] == "Learn Flask"
    assert data["goaldesc"] == "Build an API"
    assert data["userid"] == 1


def test_add_goal_missing_required_fields(client):
    """
    Should fail if required fields are missing
    """
    payload = { "goalDesc": "No name", "userId": 1 }

    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.post("/api/add_goal", json=payload)

    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data


def test_add_goal_invalid_types(client):
    """
    Should fail if wrong data types are passed
    """
    payload = {
        "goalName": 123,  # invalid type
        "goalDesc": "Test",
        "userId": 1
    }

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        
    response = client.post("/api/add_goal", json=payload)

    assert response.status_code == 400


def test_add_goal_name_too_long(client):
    """
    Should fail if goal name exceeds length
    """
    payload = {
        "goalName": "a" * 300,
        "goalDesc": "Test",
        "userId": 1
    }
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post("/api/add_goal", json=payload)

    assert response.status_code == 400


def test_add_goal_no_crash(client):
    """
    Ensure API does not crash on empty input
    """
    response = client.post("/api/add_goal", json={})

    assert response is not None
