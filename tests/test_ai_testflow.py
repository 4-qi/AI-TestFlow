from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from ai_testflow.agent.agents.api_agent import run_api_agent
from ai_testflow.agent.agents.automation_agent import run_automation_agent
from ai_testflow.agent.agents.browser_agent import run_browser_agent
from ai_testflow.agent.agents.knowledge_agent import load_knowledge_items, run_knowledge_agent
from ai_testflow.agent.agents.requirement_agent import _validate_requirement_traceability
from ai_testflow.agent.agents.test_design_agent import _validate_charter_traceability
from ai_testflow.agent.http_controller import HttpController, validate_api_action
from ai_testflow.agent.llm_client import LlmJsonParseError, LlmSettings, OpenAILlmClient, _unwrap_named_object, load_env_file
from ai_testflow.agent.orchestrator import _filter_defects_to_execution_evidence, _select_charters
from ai_testflow.browser.controller import validate_browser_action
from ai_testflow.cli import _print_agent_summary
from ai_testflow.config import AutomationConfig, BrowserRuntimeConfig, ApiRuntimeConfig, load_config


class SequenceClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def generate_json(self, **kwargs):
        self.calls.append(kwargs)
        if not self.responses:
            raise AssertionError("No fake LLM response remains")
        return self.responses.pop(0)


class DemoHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            body = b"""<!doctype html><html><head><title>Generic Form</title></head><body>
<label for='name'>Name</label><input id='name' placeholder='Your name'>
<button onclick=\"document.getElementById('result').textContent='Saved'\">Submit</button>
<p id='result'></p></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/spa":
            body = b"""<!doctype html><html><head><title>SPA Form</title></head><body>
<button onclick="history.pushState({}, '', '/next'); setTimeout(() => { document.body.innerHTML=`<h1>Next page</h1><label>Email<input></label>`; }, 100)">Continue</button>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/session":
            authenticated = "session=active" in (self.headers.get("Cookie") or "")
            self._json(200 if authenticated else 401, {"authenticated": authenticated})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/session" and payload.get("username") == "tester":
            self.send_response(200)
            self.send_header("Set-Cookie", "session=active; Path=/")
            body = json.dumps({"authenticated": True}).encode("utf-8")
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._json(400, {"authenticated": False})

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


@pytest.fixture()
def demo_server():
    server = ThreadingHTTPServer(("127.0.0.1", 0), DemoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)


def _charter(charter_id="CH-001", channel="api"):
    return {
        "charter_id": charter_id,
        "requirement_id": "REQ-001",
        "test_point_id": "TP-001",
        "goal": "验证通用测试目标",
        "channel": channel,
        "preconditions": "服务可访问",
        "test_data_strategy": "使用独立测试数据",
        "expected_result": "操作成功",
        "priority": "P0",
        "knowledge_refs": ["KB-WEB-001"],
    }


def test_load_config_reads_live_agent_runtime():
    config = load_config("ai-testflow.yml")

    assert config.project_name == "AI-TestFlow"
    assert str(config.knowledge_base.path) == "knowledge/testing"
    assert config.knowledge_base.top_k == 4
    assert config.llm_request_timeout_seconds == 120
    assert config.llm_max_retries == 1
    assert config.api_runtime.base_url == "http://127.0.0.1:5000"
    assert config.api_runtime.max_steps_per_charter == 4
    assert config.browser_runtime.observation_mode == "structured"
    assert config.browser_runtime.playwright_cwd == Path("frontend")
    assert config.browser_runtime.max_steps_per_charter == 6
    assert config.automation.output_dir == Path("ai-testflow-runs/latest/regression")
    assert config.execution_policy.max_charters_per_channel == 4


def test_agent_run_no_longer_uses_script_agent():
    source = Path("ai_testflow/agent/orchestrator.py").read_text(encoding="utf-8")

    assert "run_script_agent" not in source
    assert "run_execute_agent" not in source
    assert "run_browser_agent" in source
    assert "run_api_agent" in source
    assert source.index("[8/10] Report Agent") < source.index("[10/10] Automation Agent")


def test_prd_does_not_disclose_ground_truth_to_agent():
    prd = Path("docs/prd.md").read_text(encoding="utf-8")
    ground_truth = Path("docs/samples/demo-defect-ground-truth.md").read_text(encoding="utf-8")

    assert "后端注册接口不校验用户名长度" not in prd
    assert "后端注册接口未校验用户名长度" in ground_truth


def test_knowledge_agent_loads_and_retrieves_structured_items():
    items = load_knowledge_items(Path("knowledge/testing"))
    result = run_knowledge_agent(
        Path("knowledge/testing"),
        {
            "business_goal": "验证用户注册表单",
            "functional_requirements": [{"title": "用户名长度和必填校验"}],
            "interface_scope": ["POST /api/register"],
        },
        top_k=3,
    )

    assert len(items) == 4
    ids = [item["knowledge_id"] for item in result["selected_items"]]
    assert "KB-FORM-001" in ids
    assert all(item["matched_terms"] for item in result["selected_items"])


def test_llm_client_requires_configured_api_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY is required for agent-run"):
        OpenAILlmClient(LlmSettings(provider="openai", model="gpt-4.1-mini", api_key_env="OPENAI_API_KEY"))


def test_load_env_file_sets_missing_key(monkeypatch, tmp_path):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text("DEEPSEEK_API_KEY=local-test-key\n", encoding="utf-8")

    load_env_file(env_path)

    assert os.environ["DEEPSEEK_API_KEY"] == "local-test-key"


def test_llm_json_unwraps_named_object():
    data = {"test_charter_design": {"test_charters": []}}

    assert _unwrap_named_object("test_charter_design", data) == data["test_charter_design"]


def test_llm_json_parse_error_saves_raw_output(tmp_path):
    client = OpenAILlmClient.__new__(OpenAILlmClient)
    client._raw_output_dir = tmp_path

    with pytest.raises(LlmJsonParseError, match="test_charter_design returned invalid JSON"):
        client._parse_json_response("test_charter_design", '{"test_charters": [}')

    assert (tmp_path / "llm-raw-test_charter_design.txt").exists()


def test_http_controller_keeps_cookie_session(demo_server):
    controller = HttpController(demo_server, 5)
    login = controller.request(
        {"method": "POST", "path": "/session", "headers": {}, "query": {}, "body": {"username": "tester"}}
    )
    session = controller.request(
        {"method": "GET", "path": "/session", "headers": {}, "query": {}, "body": {}}
    )

    assert login["status_code"] == 200
    assert login["cookie_names"] == ["session"]
    assert session["response_body"] == {"authenticated": True}


def test_validate_api_action_rejects_missing_request_fields():
    with pytest.raises(ValueError, match="requires method"):
        validate_api_action({"action": "request", "path": "/health"})

    validate_api_action({"action": "request", "method": "GET", "path": "/health"})


def test_api_agent_executes_live_requests_without_generating_script(demo_server):
    client = SequenceClient(
        [
            {
                "action": "request",
                "method": "POST",
                "path": "/session",
                "headers": {},
                "query": {},
                "body": {"username": "tester"},
            },
            {
                "action": "finish",
                "status": "passed",
                "actual_result": "接口返回认证成功",
                "evidence": ["status_code=200"],
            },
        ]
    )

    result = run_api_agent(
        client,
        "prompt",
        [_charter()],
        ApiRuntimeConfig(True, demo_server, 5, 4),
    )

    assert result["status"] == "passed"
    assert result["observations"][1]["status_code"] == 200
    assert result["results"][0]["execution_id"] == "api::CH-001"
    assert len(client.calls) == 2


def test_validate_browser_action_rejects_code_or_selector_actions():
    with pytest.raises(ValueError, match="Unsupported browser action"):
        validate_browser_action({"action": "javascript", "value": "document.body"})


def test_browser_agent_observes_and_operates_generic_page(demo_server, tmp_path):
    client = SequenceClient(
        [
            {
                "action": "fill",
                "target": {"strategy": "label", "value": "Name"},
                "value": "Alice",
            },
            {
                "action": "click",
                "target": {"strategy": "role", "role": "button", "value": "Submit"},
            },
            {
                "action": "finish",
                "status": "passed",
                "actual_result": "页面显示 Saved",
                "evidence": ["visible_text contains Saved"],
            },
        ]
    )
    runtime = BrowserRuntimeConfig(
        enabled=True,
        base_url=demo_server,
        browser="chromium",
        headless=True,
        observation_mode="structured",
        max_steps_per_charter=5,
        action_timeout_ms=5000,
        playwright_cwd=Path("frontend"),
        screenshot="on_finish",
    )

    result = run_browser_agent(
        client,
        "prompt",
        [_charter("CH-WEB-001", "browser")],
        runtime,
        Path.cwd(),
        tmp_path,
    )

    assert result["status"] == "passed"
    assert any("Saved" in item["visible_text"] for item in result["observations"])
    assert result["observations"][0]["accessibility_snapshot"]
    assert result["observations"][0]["interactive_elements"]
    assert result["results"][0]["evidence"][-1].endswith("CH-WEB-001-passed.png")


def test_browser_agent_observes_settled_spa_page_after_click(demo_server, tmp_path):
    client = SequenceClient(
        [
            {"action": "navigate", "path": "/spa"},
            {
                "action": "click",
                "target": {"strategy": "role", "role": "button", "value": "Continue"},
            },
            {
                "action": "finish",
                "status": "passed",
                "actual_result": "SPA 页面完成更新",
                "evidence": ["visible_text contains Next page"],
            },
        ]
    )
    runtime = BrowserRuntimeConfig(
        enabled=True,
        base_url=demo_server,
        browser="chromium",
        headless=True,
        observation_mode="structured",
        max_steps_per_charter=4,
        action_timeout_ms=5000,
        playwright_cwd=Path("frontend"),
        screenshot="on_finish",
    )

    result = run_browser_agent(
        client,
        "prompt",
        [_charter("CH-WEB-SPA-001", "browser")],
        runtime,
        Path.cwd(),
        tmp_path,
    )

    assert result["status"] == "passed"
    click_observation = result["observations"][2]
    assert click_observation["current_url"].endswith("/next")
    assert "Next page" in click_observation["visible_text"]


def test_defect_filter_requires_failed_execution_and_product_classification():
    execution = {
        "api": {"results": [{"execution_id": "api::CH-1", "status": "failed"}]},
        "browser": {"results": [{"execution_id": "browser::CH-2", "status": "blocked"}]},
    }
    analysis = {
        "status": "has_defects",
        "classifications": [
            {
                "execution_type": "api",
                "execution_id": "api::CH-1",
                "charter_id": "CH-1",
                "classification": "product_defect",
                "reason": "违反需求",
            },
            {
                "execution_type": "browser",
                "execution_id": "browser::CH-2",
                "charter_id": "CH-2",
                "classification": "agent_blocked",
                "reason": "元素无法定位",
            },
        ],
        "defects": [
            {"bug_id": "BUG-001", "execution_id": "api::CH-1"},
            {"bug_id": "BUG-002", "execution_id": "browser::CH-2"},
        ],
    }

    filtered = _filter_defects_to_execution_evidence(analysis, execution)

    assert [item["bug_id"] for item in filtered["defects"]] == ["BUG-001"]


def test_charter_selection_prioritizes_risk_and_requirement_coverage():
    charters = [
        {"charter_id": "LOW", "requirement_id": "REQ-1", "priority": "P2"},
        {"charter_id": "HIGH-A", "requirement_id": "REQ-2", "priority": "P0"},
        {"charter_id": "HIGH-B", "requirement_id": "REQ-2", "priority": "P0"},
        {"charter_id": "MEDIUM", "requirement_id": "REQ-3", "priority": "P1"},
    ]

    selected = _select_charters(charters, 3)

    assert [item["charter_id"] for item in selected] == ["LOW", "HIGH-A", "MEDIUM"]


def test_charter_selection_rejects_unknown_priority():
    with pytest.raises(ValueError, match="Unsupported test charter priorities: High"):
        _select_charters([{"charter_id": "CH", "requirement_id": "REQ", "priority": "High"}], 1)


def test_requirement_traceability_rejects_rewritten_prd_ids():
    prd = {"functional_requirements": [{"requirement_id": "PRD-FR-003"}]}
    breakdown = {
        "requirements": [{"requirement_id": "REQ-003"}],
        "test_points": [{"requirement_id": "REQ-003", "test_point_id": "TP-003"}],
    }

    with pytest.raises(ValueError, match="preserve the exact PRD requirement_id set"):
        _validate_requirement_traceability(breakdown, prd)


def test_charter_traceability_rejects_unknown_test_point():
    breakdown = {
        "requirements": [{"requirement_id": "PRD-FR-003"}],
        "test_points": [{"requirement_id": "PRD-FR-003", "test_point_id": "TP-003"}],
    }
    design = {
        "test_charters": [
            {"charter_id": "CH-003", "requirement_id": "PRD-FR-003", "test_point_id": "TP-MISSING"}
        ]
    }

    with pytest.raises(ValueError, match="unknown test_point_id TP-MISSING"):
        _validate_charter_traceability(design, breakdown)


def test_automation_agent_only_uses_passed_execution_traces(tmp_path):
    api_execution = {
        "actions": [
            {
                "execution_id": "api::PASS",
                "charter_id": "PASS",
                "step": 1,
                "action": {"action": "request", "method": "GET", "path": "/session", "headers": {}, "query": {}, "body": {}},
            },
            {
                "execution_id": "api::FAIL",
                "charter_id": "FAIL",
                "step": 1,
                "action": {"action": "request", "method": "GET", "path": "/broken", "headers": {}, "query": {}, "body": {}},
            },
        ],
        "observations": [
            {
                "observation_id": "api::PASS::observation::1",
                "execution_id": "api::PASS",
                "step": 1,
                "status_code": 200,
                "response_body": {"ok": True},
            }
        ],
        "results": [
            {"execution_id": "api::PASS", "charter_id": "PASS", "status": "passed"},
            {"execution_id": "api::FAIL", "charter_id": "FAIL", "status": "failed"},
        ],
    }
    browser_execution = {"actions": [], "observations": [], "results": []}

    manifest = run_automation_agent(
        AutomationConfig(True, Path("runs/regression")),
        api_execution,
        browser_execution,
        "http://127.0.0.1:5000",
        "http://127.0.0.1:5173",
        Path("frontend"),
        tmp_path,
    )

    script = (tmp_path / "runs/regression/test_generated_api_regression.py").read_text(encoding="utf-8")
    assert manifest["generated_charters"] == ["PASS"]
    assert "api::PASS" in script
    assert "api::FAIL" not in script
    assert manifest["validation"][0]["status"] == "passed"


def test_agent_summary_prints_live_execution_counts(capsys):
    _print_agent_summary(
        {
            "status": "defects_found",
            "requirements_count": 2,
            "test_points_count": 3,
            "test_charters_count": 4,
            "api": {"passed": 1, "failed": 1, "blocked": 0},
            "browser": {"passed": 1, "failed": 0, "blocked": 1},
            "automation_status": "passed",
            "automated_charters_count": 2,
            "llm_metrics": {"llm_calls": 9},
            "defects": [
                {
                    "bug_id": "BUG-001",
                    "requirement_id": "REQ-001",
                    "charter_id": "CH-002",
                    "execution_type": "api",
                    "execution_id": "api::CH-002",
                }
            ],
        },
        Path("ai-testflow-runs/latest"),
    )

    output = capsys.readouterr().out
    assert "- Test charters: 4" in output
    assert "- API: passed=1 failed=1 blocked=0" in output
    assert "- Browser: passed=1 failed=0 blocked=1" in output
    assert "execution=api:api::CH-002" in output
