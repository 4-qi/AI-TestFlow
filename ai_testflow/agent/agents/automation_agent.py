from __future__ import annotations

import json
import py_compile
import subprocess
from pathlib import Path
from typing import Any

from ...config import AutomationConfig


def run_automation_agent(
    config: AutomationConfig,
    api_execution: dict[str, Any],
    browser_execution: dict[str, Any],
    api_base_url: str,
    browser_base_url: str,
    playwright_cwd: Path,
    project_root: Path,
) -> dict[str, Any]:
    output_dir = project_root / config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    if not config.enabled:
        return {"status": "disabled", "generated_charters": [], "scripts": [], "validation": []}

    generated_charters: list[str] = []
    scripts: list[str] = []
    validation: list[dict[str, Any]] = []

    api_cases = _passed_api_cases(api_execution)
    if api_cases:
        api_path = output_dir / "test_generated_api_regression.py"
        api_path.write_text(_render_api_regression(api_cases, api_base_url), encoding="utf-8")
        scripts.append(str(api_path.relative_to(project_root)))
        generated_charters.extend(case["charter_id"] for case in api_cases)
        try:
            py_compile.compile(str(api_path), doraise=True)
            validation.append({"path": str(api_path.relative_to(project_root)), "status": "passed", "type": "syntax"})
        except py_compile.PyCompileError as exc:
            validation.append(
                {"path": str(api_path.relative_to(project_root)), "status": "automation_issue", "type": "syntax", "error": str(exc)}
            )

    browser_cases = _passed_browser_cases(browser_execution)
    if browser_cases:
        browser_path = output_dir / "generated_ui_regression.spec.mjs"
        package_json = (project_root / playwright_cwd / "package.json").resolve()
        browser_path.write_text(
            _render_browser_regression(browser_cases, browser_base_url, package_json), encoding="utf-8"
        )
        scripts.append(str(browser_path.relative_to(project_root)))
        generated_charters.extend(case["charter_id"] for case in browser_cases)
        check = subprocess.run(
            ["node", "--check", str(browser_path)],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )
        validation.append(
            {
                "path": str(browser_path.relative_to(project_root)),
                "status": "passed" if check.returncode == 0 else "automation_issue",
                "type": "syntax",
                "error": check.stderr.strip(),
            }
        )

    has_issue = any(item["status"] == "automation_issue" for item in validation)
    return {
        "status": "automation_issue" if has_issue else "passed",
        "generated_charters": generated_charters,
        "scripts": scripts,
        "validation": validation,
        "policy": "passed_execution_traces_only",
    }


def _passed_api_cases(execution: dict[str, Any]) -> list[dict[str, Any]]:
    passed = {result["execution_id"]: result for result in execution.get("results", []) if result["status"] == "passed"}
    observations = {
        observation["observation_id"]: observation for observation in execution.get("observations", [])
    }
    grouped: dict[str, list[dict[str, Any]]] = {execution_id: [] for execution_id in passed}
    for action_record in execution.get("actions", []):
        execution_id = action_record["execution_id"]
        action = action_record["action"]
        if execution_id not in grouped or action["action"] != "request":
            continue
        observation_id = f"{execution_id}::observation::{action_record['step']}"
        observation = observations.get(observation_id, {})
        grouped[execution_id].append(
            {
                "action": action,
                "expected_status": observation.get("status_code"),
                "expected_body": observation.get("response_body"),
            }
        )
    return [
        {
            "charter_id": result["charter_id"],
            "execution_id": execution_id,
            "requests": grouped[execution_id],
        }
        for execution_id, result in passed.items()
        if grouped[execution_id]
    ]


def _passed_browser_cases(execution: dict[str, Any]) -> list[dict[str, Any]]:
    passed = {result["execution_id"]: result for result in execution.get("results", []) if result["status"] == "passed"}
    grouped: dict[str, list[dict[str, Any]]] = {execution_id: [] for execution_id in passed}
    final_observations: dict[str, dict[str, Any]] = {}
    for observation in execution.get("observations", []):
        execution_id = observation["execution_id"]
        if execution_id in passed:
            current = final_observations.get(execution_id)
            if current is None or observation["step"] >= current["step"]:
                final_observations[execution_id] = observation
    for action_record in execution.get("actions", []):
        execution_id = action_record["execution_id"]
        action = action_record["action"]
        if execution_id not in grouped or action["action"] == "finish" or action_record.get("error"):
            continue
        grouped[execution_id].append(action)
    return [
        {
            "charter_id": result["charter_id"],
            "execution_id": execution_id,
            "actions": grouped[execution_id],
            "final_url": final_observations.get(execution_id, {}).get("current_url"),
            "page_title": final_observations.get(execution_id, {}).get("page_title"),
        }
        for execution_id, result in passed.items()
    ]


def _render_api_regression(cases: list[dict[str, Any]], base_url: str) -> str:
    payload = repr(cases)
    return f'''from __future__ import annotations

import json
import os
from http.cookiejar import CookieJar
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

import pytest


BASE_URL = os.environ.get("AI_TESTFLOW_API_BASE_URL", {base_url!r}).rstrip("/")
CASES = {payload}


def _send(opener, action):
    query = urlencode(action.get("query") or {{}}, doseq=True)
    url = BASE_URL + action["path"] + (("?" + query) if query else "")
    body = action.get("body") or {{}}
    data = None
    headers = {{str(key): str(value) for key, value in (action.get("headers") or {{}}).items()}}
    if action["method"] in {{"POST", "PUT", "PATCH", "DELETE"}}:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    request = Request(url, data=data, headers=headers, method=action["method"])
    try:
        with opener.open(request, timeout=10) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


@pytest.mark.parametrize("case", CASES, ids=[case["charter_id"] for case in CASES])
def test_generated_api_regression(case):
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    for request_case in case["requests"]:
        status, body = _send(opener, request_case["action"])
        assert status == request_case["expected_status"]
        assert body == request_case["expected_body"]
'''


def _render_browser_regression(cases: list[dict[str, Any]], base_url: str, package_json: Path) -> str:
    payload = json.dumps(cases, ensure_ascii=False, indent=2)
    return f'''import {{ createRequire }} from 'node:module';

const requireFromProject = createRequire({json.dumps(str(package_json))});
const {{ test, expect }} = requireFromProject('@playwright/test');

const baseURL = process.env.AI_TESTFLOW_BROWSER_BASE_URL || {json.dumps(base_url)};
const cases = {payload};

function target(page, descriptor) {{
  if (descriptor.strategy === 'role') return page.getByRole(descriptor.role, {{ name: descriptor.value, exact: true }});
  if (descriptor.strategy === 'label') return page.getByLabel(descriptor.value, {{ exact: true }});
  if (descriptor.strategy === 'text') return page.getByText(descriptor.value, {{ exact: true }});
  if (descriptor.strategy === 'placeholder') return page.getByPlaceholder(descriptor.value, {{ exact: true }});
  throw new Error(`Unsupported target strategy: ${{descriptor.strategy}}`);
}}

for (const item of cases) {{
  test(item.charter_id, async ({{ page }}) => {{
    await page.goto(baseURL);
    for (const action of item.actions) {{
      if (action.action === 'navigate') await page.goto(new URL(action.path, baseURL).toString());
      else if (action.action === 'fill') await target(page, action.target).fill(action.value);
      else if (action.action === 'click') await target(page, action.target).click();
      else if (action.action === 'press') await target(page, action.target).press(action.key);
      else if (action.action === 'select_option') await target(page, action.target).selectOption(action.option);
      else if (action.action === 'check') await target(page, action.target).check();
      else if (action.action === 'scroll') await page.mouse.wheel(0, action.direction === 'down' ? 700 : -700);
      else if (action.action === 'wait') await page.waitForTimeout(action.milliseconds);
    }}
    if (item.final_url) await expect(page).toHaveURL(item.final_url);
    if (item.page_title) await expect(page).toHaveTitle(item.page_title);
  }});
}}
'''
