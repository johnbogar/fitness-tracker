import pytest
from app import app
from models.goal import Goal
from db import SessionLocal


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"

    with app.test_client() as client:
        yield client


def create_test_goal(user_id=1):
    """
    Function for creating a test goal
    """
    db = SessionLocal()
    goal = Goal(
        goalname="Original Goal",
        goaldesc="Original Desc",
        userid=user_id
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    db.close()
    return goal


def test_edit_goal_success(client):
    """
    Function for testing succeessful update
    """
    goal = create_test_goal()

    with client.session_transaction() as sess:
        sess["user_id"] = goal.userid

    payload = {
        "goalId": goal.id,
        "goalName": "Updated Goal",
        "goalDesc": "Updated Desc",
        "endDate": "2026-06-01"
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 200

    data = response.get_json()

    assert data["message"] == "Goal updated successfully"
    assert data["goal"]["goalname"] == "Updated Goal"
    assert data["goal"]["goaldesc"] == "Updated Desc"


def test_edit_goal_unauthorized(client):
    """
    Function to test unauthorized payload
    """
    payload = {
        "goalId": 1,
        "goalName": "Updated"
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 401

    data = response.get_json()
    assert "error" in data


def test_edit_goal_not_owner(client):
    """
    Function to test that the user is the one who owns the goal
    """
    goal = create_test_goal(user_id=1)

    with client.session_transaction() as sess:
        sess["user_id"] = 2  # different user

    payload = {
        "goalId": goal.id,
        "goalName": "Hacked"
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 401


def test_edit_goal_not_found(client):
    """
    Function to test if goal not found
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "goalId": 9999,
        "goalName": "Doesn't exist"
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 404


def test_edit_goal_missing_fields(client):
    """
    Test case for missing fields
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.put("/api/edit_goal", json={})

    assert response.status_code == 400


def test_edit_goal_invalid_types(client):
    """
    Function test case for invalid types
    """
    goal = create_test_goal()

    with client.session_transaction() as sess:
        sess["user_id"] = goal.userid

    payload = {
        "goalId": goal.id,
        "goalName": 123,  # invalid
        "goalDesc": "Valid"
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 400


def test_edit_goal_name_too_long(client):
    """
    Test case if goal name is too long
    """
    goal = create_test_goal()

    with client.session_transaction() as sess:
        sess["user_id"] = goal.userid

    payload = {
        "goalId": goal.id,
        "goalName": "a" * 300
    }

    response = client.put("/api/edit_goal", json=payload)

    assert response.status_code == 400


def test_edit_goal_no_crash(client):
    """
    Ensure API does not crash on bad input
    """
    response = client.put("/api/edit_goal", json=None)

    assert response is not None