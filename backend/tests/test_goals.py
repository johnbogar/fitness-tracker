import pytest 
from app import app

# to use, enter the venv and run 'python -m pytest'

@pytest.fixture
def client():
    """
    Simulates a browser making API requests without running the server
    """
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client

def test_view_goals_status(client):
    """
    Tests whether api can be reached
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/api/view_goals")
    assert response.status_code == 200

def test_goals_returns_list(client):
    """
    Checks that response is a list
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("/api/view_goals")
    data = response.get_json()
    assert isinstance(data, list)

def test_goal_structure(client):
    """
    Tests that the returned goals are in the correct format
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.get("/api/view_goals")
    data = response.get_json()

    #make sure there is data
    if len(data) > 0:
        goal = data[0]

        assert "id" in goal
        assert "goalname" in goal
        assert "goaldesc" in goal
        assert "userid" in goal

def test_api_not_crashing(client):
    """
    Tests that the api has not crashed
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1
    response = client.get("api/view_goals")
    assert response.data is not None

