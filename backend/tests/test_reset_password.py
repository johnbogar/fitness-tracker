from db import conn
from sqlalchemy import text
from werkzeug.security import generate_password_hash
import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "testsecret"

    with app.test_client() as client:
        yield client
        
def create_user_with_password():
    hashed = generate_password_hash("OldPass123!")

    conn.execute(text('''
        INSERT INTO "Users" (firstname, lastname, email, password)
        VALUES ('Reset', 'User', 'reset@example.com', :password)
    '''), {"password": hashed})

    conn.commit()

    user = conn.execute(text(
        'SELECT id FROM "Users" WHERE email = :email'),
        {"email": "reset@example.com"}
    ).fetchone()

    return user.id


def test_reset_password_success(client):
    user_id = create_user_with_password()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.put("/api/reset-password", json={
        "currentPassword": "OldPass123!",
        "newPassword": "NewPass123!"
    })

    assert response.status_code == 200

    conn.execute(text('DELETE FROM "Users" WHERE id = :id'), {"id": user_id})
    conn.commit()


def test_reset_password_wrong_current_password(client):
    user_id = create_user_with_password()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.put("/api/reset-password", json={
        "currentPassword": "WrongPass",
        "newPassword": "NewPass123!"
    })

    assert response.status_code == 401

    conn.execute(text('DELETE FROM "Users" WHERE id = :id'), {"id": user_id})
    conn.commit()


def test_reset_password_not_authenticated(client):
    response = client.put("/api/reset-password", json={
        "currentPassword": "x",
        "newPassword": "y"
    })

    assert response.status_code == 401


def test_reset_password_missing_fields(client):
    user_id = create_user_with_password()

    with client.session_transaction() as sess:
        sess["user_id"] = user_id

    response = client.put("/api/reset-password", json={})

    assert response.status_code == 400

    conn.execute(text('DELETE FROM "Users" WHERE id = :id'), {"id": user_id})
    conn.commit()