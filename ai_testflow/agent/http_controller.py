from __future__ import annotations

import json
import time
from http.cookiejar import CookieJar
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener


class HttpController:
    def __init__(self, base_url: str, timeout_seconds: float):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._cookie_jar = CookieJar()
        self._opener = build_opener(HTTPCookieProcessor(self._cookie_jar))

    def request(self, action: dict[str, Any]) -> dict[str, Any]:
        query = action.get("query") or {}
        query_string = urlencode(query, doseq=True)
        path = action["path"]
        url = f"{self._base_url}{path}"
        if query_string:
            url = f"{url}?{query_string}"
        body = action.get("body") or {}
        method = action["method"]
        data = None
        headers = {str(key): str(value) for key, value in (action.get("headers") or {}).items()}
        if method in {"POST", "PUT", "PATCH", "DELETE"}:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        request = Request(url, data=data, headers=headers, method=method)
        started = time.monotonic()
        try:
            with self._opener.open(request, timeout=self._timeout_seconds) as response:
                response_body = response.read()
                status_code = response.status
                response_headers = dict(response.headers.items())
        except HTTPError as exc:
            response_body = exc.read()
            status_code = exc.code
            response_headers = dict(exc.headers.items())
        except URLError as exc:
            duration_ms = round((time.monotonic() - started) * 1000, 2)
            return {
                "request": _request_record(method, path, query, body),
                "transport_error": str(exc.reason),
                "duration_ms": duration_ms,
            }
        duration_ms = round((time.monotonic() - started) * 1000, 2)
        text = response_body.decode("utf-8", errors="replace")
        try:
            parsed_body: Any = json.loads(text)
        except json.JSONDecodeError:
            parsed_body = text
        return {
            "request": _request_record(method, path, query, body),
            "status_code": status_code,
            "response_headers": response_headers,
            "response_body": parsed_body,
            "duration_ms": duration_ms,
            "cookie_names": sorted(cookie.name for cookie in self._cookie_jar),
        }


def validate_api_action(action: dict[str, Any]) -> None:
    action_name = action.get("action")
    if action_name == "request":
        for key in ["method", "path"]:
            if key not in action:
                raise ValueError(f"API request action requires {key}")
        for key in ["headers", "query", "body"]:
            if key in action and not isinstance(action[key], dict):
                raise ValueError(f"API request action {key} must be an object")
        if not str(action["path"]).startswith("/"):
            raise ValueError("API request action path must start with /")
        return
    if action_name == "finish":
        for key in ["status", "actual_result", "evidence"]:
            if key not in action:
                raise ValueError(f"API finish action requires {key}")
        return
    raise ValueError(f"Unsupported API action: {action_name}")


def _request_record(method: str, path: str, query: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    return {"method": method, "path": path, "query": query, "body": body}
