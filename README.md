# AI-TestFlow

自动化测试全流程插件原型 + React Flask 登录注册 Demo。

本仓库用于验证从 PRD 分析、需求拆解、测试用例设计、用例执行、测试报告生成到 Bug 单提交的最小闭环。

## 1. 项目结构

```text
AI-TestFlow/
  backend/
    app.py
    requirements.txt
    tests/test_api.py
  frontend/
    package.json
    src/
  docs/
    project-introduction.md
    task-analysis-and-workflow.md
    prd.md
    requirement-spec.md
    test-cases.md
    manual-test-execution.md
    api-test-execution.md
    test-report.md
    bug-report.md
    plugin-prototype-design.md
```

## 2. 环境

Python 环境：

```bash
conda activate AI-TestFlow
python --version
```

已验证 Python 版本：

```text
Python 3.10.20
```

Node 环境：

```bash
node --version
npm --version
```

已验证版本：

```text
Node v22.19.0
npm 10.9.3
```

## 3. 安装依赖

后端依赖：

```bash
conda run -n AI-TestFlow pip install -r backend/requirements.txt
```

前端依赖：

```bash
cd frontend
npm install
```

## 4. 启动后端

在项目根目录执行：

```bash
conda run --no-capture-output -n AI-TestFlow python backend/app.py
```

后端地址：

```text
http://127.0.0.1:5000
```

说明：

后端启动后会一直占用当前终端，这是正常现象。看到 `Backend URL: http://127.0.0.1:5000` 后，保持该终端运行，再打开一个新终端启动前端。停止后端时，在后端终端按 `Ctrl + C`。

## 5. 启动前端

在 `frontend` 目录执行：

```bash
npm run dev
```

前端地址：

```text
http://127.0.0.1:5173
```

## 6. 运行测试

在项目根目录执行：

```bash
conda run -n AI-TestFlow python -m pytest -q backend/tests
```

已验证结果：

```text
12 passed in 0.93s
```

## 7. 预埋缺陷

需求要求：

```text
用户名长度必须大于等于 6 位。
```

当前系统保留的预埋缺陷：

```text
后端注册接口未校验用户名长度，短用户名可以注册成功。
```

追踪关系：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

## 8. 文档入口

| 文档 | 路径 |
| --- | --- |
| 项目介绍 | `docs/project-introduction.md` |
| 任务分析与流程 | `docs/task-analysis-and-workflow.md` |
| PRD | `docs/prd.md` |
| 需求规格说明书 | `docs/requirement-spec.md` |
| 测试用例 | `docs/test-cases.md` |
| 手工测试执行记录 | `docs/manual-test-execution.md` |
| 接口自动化测试执行记录 | `docs/api-test-execution.md` |
| 测试报告 | `docs/test-report.md` |
| Bug 单 | `docs/bug-report.md` |
| 插件原型设计 | `docs/plugin-prototype-design.md` |
