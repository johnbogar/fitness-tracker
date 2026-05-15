import pytest
from app import app
from models.goal import Goal
from db import SessionLocal


@pytest.fixture
def client():
    """
    Define the client
    """
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"

    with app.test_client() as client:
        with app.app_context():
            yield client


def create_test_goal():
    """
    Create a test goal for use
    """
    db = SessionLocal()

    goal = Goal(
        goalname="Test Goal",
        goaldesc="To be deleted",
        userid=1
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)
    db.close()

    return goal

def test_delete_goal_success(client):
    """
    Test goal deleted successfully
    """

    goal = create_test_goal()

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {
        "goalId": goal.id
    }

    response = client.post("/api/delete_goal", json=payload)

    assert response.status_code == 200

    data = response.get_json()
    assert data["message"] == "Goal deleted successfully"
    assert data["deletedGoalId"] == goal.id

def test_delete_goal_unauthorized(client):
    """
    Test if it is unauthorized
    """

    payload = {"goalId": 1}

    response = client.post("/api/delete_goal", json=payload)

    assert response.status_code == 401

    data = response.get_json()
    assert "error" in data


def test_delete_goal_invalid_json(client):
    """
    Test that it fails if Json not sent
    """

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.post("/api/delete_goal")

    assert response.status_code == 400

    data = response.get_json()
    assert "error" in data


def test_delete_goal_not_found(client):
    """
    Tests invalid goal
    """

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    payload = {"goalId": 999999}

    response = client.post("/api/delete_goal", json=payload)

    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Goal not found"