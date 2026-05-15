from db import conn
from sqlalchemy import text
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"

    with app.test_client() as client:
        yield client


def create_test_user():
    conn.execute(text('''
        INSERT INTO "Users" (firstname, lastname, email, password)
        VALUES ('Test', 'User', 'test_edit@example.com', 'hashed')
    '''))
    conn.commit()

    user = conn.execute(
        text('SELECT id FROM "Users" WHERE email = :email'),
        {"email": "test_edit@example.com"}
    ).fetchone()

    return user.id


def test_edit_user_success(client):
    user_id = create_test_user()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.put("/api/edit-user", json={
        "firstname": "Updated",
        "lastname": "Name"
    })

    assert response.status_code == 200
    data = response.get_json()

    assert data["message"] == "User updated successfully"
    assert data["user"]["name"] == "Updated Name"

    # teardown
    conn.execute(text('DELETE FROM "Users" WHERE id = :id'), {"id": user_id})
    conn.commit()


def test_edit_user_not_authenticated(client):
    response = client.put("/api/edit-user", json={
        "firstname": "Test",
        "lastname": "User"
    })

    assert response.status_code == 401


def test_edit_user_missing_fields(client):
    user_id = create_test_user()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.put("/api/edit-user", json={})

    assert response.status_code == 400

    conn.execute(text('DELETE FROM "Users" WHERE id = :id'), {"id": user_id})
    conn.commit()


def test_edit_user_no_crash(client):
    """
    Make sure API doesn't crash on bad input
    """
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    response = client.put("/api/edit-user", json=None)

    assert response is not None