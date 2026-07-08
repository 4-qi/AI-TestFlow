from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATABASE = BASE_DIR / "instance" / "app.db"


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        DATABASE=str(DEFAULT_DATABASE),
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if test_config:
        app.config.update(test_config)

    CORS(app, supports_credentials=True, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    init_db(app.config["DATABASE"])

    @app.post("/api/register")
    def register():
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))
        confirm_password = str(payload.get("confirm_password", ""))

        if not username:
            return api_error("用户名不能为空", 400)

        # Deliberately keep REG-002 missing for the planned business-rule defect.
        if not password:
            return api_error("密码不能为空", 400)

        if confirm_password != password:
            return api_error("两次输入的密码不一致", 400)

        try:
            with get_connection(app.config["DATABASE"]) as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                    (
                        username,
                        generate_password_hash(password),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
        except sqlite3.IntegrityError:
            return api_error("用户名已存在", 409)

        return api_success("注册成功", {"username": username})

    @app.post("/api/login")
    def login():
        payload = request.get_json(silent=True) or {}
        username = str(payload.get("username", "")).strip()
        password = str(payload.get("password", ""))

        if not username:
            return api_error("用户名不能为空", 400)

        if not password:
            return api_error("密码不能为空", 400)

        with get_connection(app.config["DATABASE"]) as conn:
            user = conn.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,),
            ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            return api_error("用户名或密码错误", 401)

        session["username"] = user["username"]
        return api_success("登录成功", {"username": user["username"]})

    @app.get("/api/me")
    def me():
        username = session.get("username")
        if not username:
            return api_error("用户未登录", 401)

        return api_success("获取当前用户成功", {"username": username})

    @app.post("/api/logout")
    def logout():
        session.pop("username", None)
        return api_success("退出登录成功", None)

    return app


def get_connection(database: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(database: str) -> None:
    with get_connection(database) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def api_success(message: str, data: Any):
    return jsonify({"success": True, "message": message, "data": data})


def api_error(message: str, status_code: int):
    return jsonify({"success": False, "message": message, "data": None}), status_code


app = create_app()


if __name__ == "__main__":
    print("AI-TestFlow Flask backend is starting...", flush=True)
    print("Backend URL: http://127.0.0.1:5000", flush=True)
    print("Health check: http://127.0.0.1:5000/api/me", flush=True)
    print("Stop backend: press Ctrl + C in this terminal", flush=True)
    print("Start frontend in another terminal: cd frontend && npm run dev", flush=True)
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
