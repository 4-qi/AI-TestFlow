from __future__ import annotations

import json
import pprint
import re
from typing import Any


def render_generated_api_tests(api_tests: list[dict[str, Any]], runtime: dict[str, str] | None = None) -> str:
    runtime = runtime or {"mode": "flask_app", "app_factory": "backend.app:create_app"}
    header = _render_api_header(runtime)
    return header + "\n\n" + _render_api_cases(api_tests)


def render_generated_playwright_tests(ui_tests: list[dict[str, Any]]) -> str:
    payload = json.dumps(ui_tests, ensure_ascii=False, indent=2)
    return PLAYWRIGHT_HEADER + f"\nconst cases = {payload};\n\n" + PLAYWRIGHT_RUNNER


def _render_api_cases(api_tests: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for index, api_test in enumerate(api_tests, start=1):
        function_name = generated_api_test_name(api_test, index)
        payload = pprint.pformat(api_test, sort_dicts=False, width=100)
        lines.append(
            f'''def {function_name}(client):
    case = {payload}
    for setup_action in case["setup_api_actions"]:
        setup_response = _send(client, setup_action)
        assert setup_response.status_code == setup_action["expected_status"]
    response = _send(client, case)
    assert response.status_code == case["expected_status"]
    body = response.get_json(silent=True) or {{}}
    _assert_json_contains(body, case["expected_json_contains"])
'''
        )
    return "\n".join(lines).rstrip() + "\n"


def generated_api_test_name(api_test: dict[str, Any], index: int = 1) -> str:
    name_source = f"{api_test.get('test_case_id', '')}_{api_test.get('name', '')}".strip("_")
    return _python_test_name(name_source or f"api_case_{index}")


def _python_test_name(value: str) -> str:
    normalized = re.sub(r"[^0-9A-Za-z_]+", "_", value).strip("_").lower()
    if not normalized:
        normalized = "generated_api_case"
    if normalized[0].isdigit():
        normalized = f"case_{normalized}"
    if not normalized.startswith("test_"):
        normalized = f"test_generated_{normalized}"
    return normalized


def _render_api_header(runtime: dict[str, str]) -> str:
    mode = runtime.get("mode", "flask_app")
    if mode == "flask_app":
        app_factory = runtime["app_factory"]
        module_name, factory_name = app_factory.split(":", 1)
        return FLASK_API_HEADER.replace("__MODULE_NAME__", module_name).replace("__FACTORY_NAME__", factory_name)
    if mode == "http":
        base_url = runtime["base_url"].rstrip("/")
        return HTTP_API_HEADER.format(base_url=base_url)
    raise ValueError(f"Unsupported api_test_runtime mode: {mode}")


FLASK_API_HEADER = '''from __future__ import annotations

import importlib
from pathlib import Path

import pytest


@pytest.fixture()
def client(tmp_path: Path):
    module = importlib.import_module("__MODULE_NAME__")
    create_app = getattr(module, "__FACTORY_NAME__")
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "generated-test.db"),
            "SECRET_KEY": "generated-test-secret-key",
        }
    )
    return app.test_client()


def _send(client, case):
    method = case["method"].lower()
    request = getattr(client, method)
    if method in {"post", "put", "patch", "delete"}:
        return request(case["path"], json=case["json_body"])
    return request(case["path"])


def _assert_json_contains(actual, expected):
    for key, expected_value in expected.items():
        assert key in actual
        if isinstance(expected_value, dict):
            _assert_json_contains(actual[key], expected_value)
        else:
            assert actual[key] == expected_value
'''


HTTP_API_HEADER = '''from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError

import pytest


@pytest.fixture()
def client():
    return "{base_url}"


class HttpResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def get_json(self, silent=True):
        try:
            return json.loads(self._body.decode("utf-8"))
        except json.JSONDecodeError:
            if silent:
                return None
            raise


def _send(client, case):
    url = client + case["path"]
    data = None
    headers = {{}}
    if case["method"] in {{"POST", "PUT", "PATCH", "DELETE"}}:
        data = json.dumps(case["json_body"]).encode("utf-8")
        headers["Content-Type"] = "application/json"
    http_request = request.Request(url, data=data, headers=headers, method=case["method"])
    try:
        with request.urlopen(http_request) as response:
            return HttpResponse(response.status, response.read())
    except HTTPError as exc:
        return HttpResponse(exc.code, exc.read())


def _assert_json_contains(actual, expected):
    for key, expected_value in expected.items():
        assert key in actual
        if isinstance(expected_value, dict):
            _assert_json_contains(actual[key], expected_value)
        else:
            assert actual[key] == expected_value
'''


PLAYWRIGHT_HEADER = """import { test, expect } from '@playwright/test';
"""


PLAYWRIGHT_RUNNER = """async function fillByLabel(page, label, value) {
  const exactLocator = page.getByLabel(label, { exact: true });
  if (await exactLocator.count()) {
    await exactLocator.first().fill(value);
    return;
  }
  await page.getByLabel(label).first().fill(value);
}

async function clickByRole(page, role, name) {
  const exactLocator = page.getByRole(role, { name, exact: true });
  if (await exactLocator.count()) {
    await exactLocator.first().click();
    return;
  }
  const roleLocator = page.getByRole(role, { name });
  if (await roleLocator.count()) {
    await roleLocator.first().click();
    return;
  }
  if (role === 'button') {
    const buttonTextLocator = page.locator('button').filter({ hasText: name });
    if (await buttonTextLocator.count()) {
      await buttonTextLocator.first().click();
      return;
    }
  }
  await page.getByText(name).first().click();
}

async function expectText(page, text) {
  const exactLocator = page.getByText(text, { exact: true }).first();
  try {
    await expect(exactLocator).toBeVisible({ timeout: 1000 });
    return;
  } catch (error) {
    await expect(page.getByText(text).first()).toBeVisible();
  }
}

for (const item of cases) {
  test(item.title, async ({ page }) => {
    for (const action of item.actions) {
      if (action.action === 'goto') {
        await page.goto(action.url);
      } else if (action.action === 'fill_label') {
        await fillByLabel(page, action.label, action.value);
      } else if (action.action === 'click_role') {
        await clickByRole(page, action.role, action.name);
      } else if (action.action === 'expect_text') {
        await expectText(page, action.text);
      } else if (action.action === 'expect_url') {
        await expect(page).toHaveURL(new RegExp(action.pattern));
      } else {
        throw new Error(`Unsupported UI action: ${action.action}`);
      }
    }
  });
}
"""
