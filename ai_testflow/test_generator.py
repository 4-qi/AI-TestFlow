from __future__ import annotations


def render_generated_api_tests(test_cases: list[dict[str, str]]) -> str:
    test_ids = {item["test_case_id"] for item in test_cases}
    sections = [
        HEADER,
        _case("TC-REG-001", test_ids, test_cases, TEST_REGISTER_SUCCESS, ["注册成功"]),
        _case("TC-REG-002", test_ids, test_cases, TEST_REGISTER_REQUIRES_USERNAME, ["用户名为空"]),
        _case("TC-REG-003", test_ids, test_cases, TEST_REGISTER_REJECTS_SHORT_USERNAME, ["用户名长度", "小于6"]),
        _case("TC-REG-004", test_ids, test_cases, TEST_REGISTER_REQUIRES_PASSWORD, ["密码为空"]),
        _case("TC-REG-005", test_ids, test_cases, TEST_REGISTER_REQUIRES_MATCHING_PASSWORDS, ["确认密码", "不一致"]),
        _case("TC-REG-006", test_ids, test_cases, TEST_REGISTER_REJECTS_DUPLICATE_USERNAME, ["重复用户名"]),
        _case("TC-LOGIN-001", test_ids, test_cases, TEST_LOGIN_SUCCESS, ["登录成功"]),
        _case("TC-LOGIN-002", test_ids, test_cases, TEST_LOGIN_REJECTS_WRONG_PASSWORD, ["密码错误"]),
        _case("TC-LOGIN-003", test_ids, test_cases, TEST_LOGIN_REJECTS_UNKNOWN_USER, ["不存在", "用户名"]),
        _case("TC-ME-001", test_ids, test_cases, TEST_ME_REQUIRES_LOGIN, ["未登录"]),
        _case("TC-ME-002", test_ids, test_cases, TEST_ME_RETURNS_LOGGED_IN_USER, ["首页显示用户名"]),
        _case("TC-LOGOUT-001", test_ids, test_cases, TEST_LOGOUT_CLEARS_LOGIN, ["退出登录"]),
    ]
    return "\n\n".join(section for section in sections if section).rstrip() + "\n"


def _case(test_case_id: str, test_ids: set[str], test_cases: list[dict[str, str]], body: str, keywords: list[str]) -> str:
    if test_case_id not in test_ids:
        if not any(_matches_case(item, keywords) for item in test_cases):
            return ""
    return body


def _matches_case(test_case: dict[str, str], keywords: list[str]) -> bool:
    searchable = " ".join(
        str(test_case.get(key, ""))
        for key in ["title", "test_data", "expected_result", "precondition"]
    )
    normalized = searchable.replace(" ", "")
    return all(keyword in normalized for keyword in keywords)


HEADER = '''from __future__ import annotations

from pathlib import Path

import pytest

from backend.app import create_app


@pytest.fixture()
def client(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "generated-test.db"),
            "SECRET_KEY": "generated-test-secret-key",
        }
    )
    return app.test_client()
'''


TEST_REGISTER_SUCCESS = '''def test_generated_register_success(client):
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "password": "Password123",
            "confirm_password": "Password123",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "注册成功"
'''


TEST_REGISTER_REQUIRES_USERNAME = '''def test_generated_register_requires_username(client):
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
'''


TEST_REGISTER_REJECTS_SHORT_USERNAME = '''def test_generated_register_rejects_short_username(client):
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
'''


TEST_REGISTER_REQUIRES_PASSWORD = '''def test_generated_register_requires_password(client):
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
'''


TEST_REGISTER_REQUIRES_MATCHING_PASSWORDS = '''def test_generated_register_requires_matching_passwords(client):
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
'''


TEST_REGISTER_REJECTS_DUPLICATE_USERNAME = '''def test_generated_register_rejects_duplicate_username(client):
    payload = {
        "username": "testuser",
        "password": "Password123",
        "confirm_password": "Password123",
    }
    client.post("/api/register", json=payload)

    response = client.post("/api/register", json=payload)

    assert response.status_code == 409
    assert response.get_json()["message"] == "用户名已存在"
'''


TEST_LOGIN_SUCCESS = '''def test_generated_login_success(client):
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
    assert response.get_json()["message"] == "登录成功"
'''


TEST_LOGIN_REJECTS_WRONG_PASSWORD = '''def test_generated_login_rejects_wrong_password(client):
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
'''


TEST_LOGIN_REJECTS_UNKNOWN_USER = '''def test_generated_login_rejects_unknown_user(client):
    response = client.post(
        "/api/login",
        json={
            "username": "missinguser",
            "password": "Password123",
        },
    )

    assert response.status_code == 401
    assert response.get_json()["message"] == "用户名或密码错误"
'''


TEST_ME_REQUIRES_LOGIN = '''def test_generated_me_requires_login(client):
    response = client.get("/api/me")

    assert response.status_code == 401
    assert response.get_json()["message"] == "用户未登录"
'''


TEST_ME_RETURNS_LOGGED_IN_USER = '''def test_generated_me_returns_logged_in_user(client):
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
'''


TEST_LOGOUT_CLEARS_LOGIN = '''def test_generated_logout_clears_login(client):
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
'''
