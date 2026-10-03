import pytest
from app import app, users


@pytest.fixture
def client():
    app.config["TESTING"] = True

    users.clear()

    with app.test_client() as client:
        yield client


def test_registration_hashes_password(client):
    response = client.post(
        "/register",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    assert response.status_code == 200
    assert "student1" in users
    assert users["student1"] != "StrongPass123"


def test_login_success(client):
    client.post(
        "/register",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    assert response.status_code == 302
    assert response.location.endswith("/dashboard")


def test_invalid_login_uses_generic_error(client):
    client.post(
        "/register",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    response = client.post(
        "/login",
        data={
            "username": "student1",
            "password": "WrongPassword"
        }
    )

    assert response.status_code == 401
    assert response.data == b"Invalid username or password."


def test_protected_page_requires_login(client):
    response = client.get("/dashboard")

    assert response.status_code == 302
    assert response.location.endswith("/login")


def test_logout(client):
    client.post(
        "/register",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    client.post(
        "/login",
        data={
            "username": "student1",
            "password": "StrongPass123"
        }
    )

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.location.endswith("/login")


def test_short_password_rejected(client):
    response = client.post(
        "/register",
        data={
            "username": "student1",
            "password": "123"
        }
    )

    assert response.status_code == 400