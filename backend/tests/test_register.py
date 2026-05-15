import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_register_success(client):
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "newuser_test@example.com",
        "password": "SecurePass123!"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 201
    assert response.get_json()["message"] == "Account created successfully"

    # Teardown: remove the test user so the test can run again cleanly
    from db import conn
    from sqlalchemy import text
    conn.execute(text('DELETE FROM "Users" WHERE email = :email'), {"email": "newuser_test@example.com"})
    conn.commit()


def test_register_duplicate_email(client):
    """
    Test Case 2 - Duplicate email: Should display specific error message.
    """
    payload = {
        "firstname": "Jane",
        "lastname": "Doe",
        "email": "duplicate@example.com",
        "password": "SecurePass123!"
    }
    # Register once
    client.post("/api/register", json=payload)
    # Try to register again with the same email
    response = client.post("/api/register", json=payload)

    assert response.status_code == 409
    data = response.get_json()
    assert data["error"] == "An account with the following email already exists"


def test_register_missing_fields(client):
    """
    Test Case 3 - Missing inputs: Should return validation error and not create account.
    """
    # Missing password
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "missing@example.com"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_register_invalid_email_format(client):
    """
    Test Case 3 - Invalid email: Should return validation error and not create account.
    """
    payload = {
        "firstname": "John",
        "lastname": "Doe",
        "email": "notanemail",
        "password": "SecurePass123!"
    }
    response = client.post("/api/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_register_no_crash(client):
    """
    Ensure the register endpoint does not crash on empty input.
    """
    response = client.post("/api/register", json={})
    assert response is not None
    assert response.status_code == 400
