from __future__ import annotations

from pathlib import Path
from typing import Any

from ...test_generator import render_generated_api_tests
from ..llm_client import OpenAILlmClient
from ..schemas import SCRIPT_PLAN_SCHEMA, validate_required_keys


def run_script_agent(
    client: OpenAILlmClient,
    prompt: str,
    test_cases: list[dict[str, Any]],
    api_target: Path,
    playwright_target: Path,
) -> dict[str, Any]:
    script_plan = client.generate_json(
        name="script_plan",
        system_prompt=prompt,
        user_prompt=f"请基于测试用例生成接口自动化和页面自动化脚本计划。\n\n{test_cases}",
        schema=SCRIPT_PLAN_SCHEMA,
    )
    validate_required_keys("script_plan", script_plan, SCRIPT_PLAN_SCHEMA)

    api_case_ids = set(script_plan["api_test_case_ids"])
    api_cases = [case for case in test_cases if case["test_case_id"] in api_case_ids]
    api_script = render_generated_api_tests(api_cases)
    playwright_script = _render_playwright_tests(script_plan["playwright_flows"])
    api_target.parent.mkdir(parents=True, exist_ok=True)
    playwright_target.parent.mkdir(parents=True, exist_ok=True)
    api_target.write_text(api_script, encoding="utf-8")
    playwright_target.write_text(playwright_script, encoding="utf-8")
    return {
        "script_plan": script_plan,
        "api_script": str(api_target),
        "playwright_script": str(playwright_target),
    }


def _render_playwright_tests(flows: list[dict[str, Any]]) -> str:
    sections = ["import { test, expect } from '../../frontend/node_modules/@playwright/test';\n"]
    flow_ids = {flow["flow_id"] for flow in flows}
    if "PW-REG-001" in flow_ids:
        sections.append(SHORT_USERNAME_FLOW)
    if "PW-AUTH-001" in flow_ids:
        sections.append(AUTH_FLOW)
    return "\n".join(sections).rstrip() + "\n"


SHORT_USERNAME_FLOW = """test('short username registration should be rejected', async ({ page }) => {
  await page.goto('/register');
  await page.getByLabel('用户名').fill('abc');
  await page.getByLabel('密码').fill('Password123');
  await page.getByLabel('确认密码').fill('Password123');
  await page.getByRole('button', { name: '注册' }).click();
  await expect(page.getByText('用户名长度不能少于6位')).toBeVisible();
});
"""


AUTH_FLOW = """test('register login home logout flow', async ({ page }) => {
  const username = `testuser${Date.now()}`;
  await page.goto('/register');
  await page.getByLabel('用户名').fill(username);
  await page.getByLabel('密码').fill('Password123');
  await page.getByLabel('确认密码').fill('Password123');
  await page.getByRole('button', { name: '注册' }).click();
  await page.goto('/login');
  await page.getByLabel('用户名').fill(username);
  await page.getByLabel('密码').fill('Password123');
  await page.getByRole('button', { name: '登录' }).click();
  await expect(page.getByText(username)).toBeVisible();
  await page.getByRole('button', { name: '退出登录' }).click();
  await expect(page).toHaveURL(/login/);
});
"""
