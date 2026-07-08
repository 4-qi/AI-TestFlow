from __future__ import annotations

from pathlib import Path

import pytest

from backend.app import create_app


@pytest.fixture()
def client(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "SECRET_KEY": "test-secret-key",
        }
    )
    return app.test_client()


def test_register_success(client):
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "message": "注册成功",
        "data": {"username": "testuser"},
    }


def test_register_requires_username(client):
    response = client.post(
        "/api/register",
        json={
            "username": "",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "用户名不能为空"


def test_register_requires_password(client):
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "",
            "confirm_password": "",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "密码不能为空"


def test_register_requires_matching_passwords(client):
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password456",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "两次输入的密码不一致"


def test_register_rejects_duplicate_username(client):
    payload = {
        "username": "testuser",
        "password": "Password123",
        "confirm_password": "Password123",
    }
    client.post("/api/register", json=payload)

    response = client.post("/api/register", json=payload)

    assert response.status_code == 409
    assert response.get_json()["message"] == "用户名已存在"


def test_register_rejects_short_username_by_requirement(client):
    response = client.post(
        "/api/register",
        json={
            "username": "abc",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "用户名长度不能少于6位"


def test_login_success(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    response = client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "Password123",
        },
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "success": True,
        "message": "登录成功",
        "data": {"username": "testuser"},
    }


def test_login_rejects_wrong_password(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    response = client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "用户名或密码错误"


def test_login_rejects_unknown_user(client):
    response = client.post(
        "/api/login",
        json={
            "username": "missinguser",
            "password": "Password123",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "用户名或密码错误"


def test_me_requires_login(client):
    response = client.get("/api/me")

    assert response.status_code == 401
    assert response.get_json()["message"] == "用户未登录"


def test_me_returns_logged_in_user(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "Password123",
        },
    )

    response = client.get("/api/me")

    assert response.status_code == 200
    assert response.get_json()["data"] == {"username": "testuser"}


def test_logout_clears_login(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )
    client.post(
        "/api/login",
        json={
            "username": "testuser",
            "password": "Password123",
        },
    )

    logout_response = client.post("/api/logout")
    me_response = client.get("/api/me")

    assert logout_response.status_code == 200
    assert logout_response.get_json()["message"] == "退出登录成功"
    assert me_response.status_code == 401

