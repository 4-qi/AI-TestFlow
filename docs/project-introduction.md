# AI-TestFlow 项目介绍

## 1. 项目一句话说明

AI-TestFlow 是一个用于验证“AI 驱动自动化测试全流程”的最小原型项目。

它由四部分组成：

1. 一个可运行的 React + Flask 登录注册 Demo 系统。
2. 一套围绕该 Demo 系统编写的测试全流程文档，包括 PRD、需求规格、测试用例、执行记录、测试报告、Bug 单和插件原型设计。
3. 一个 `ai_testflow` CLI + `skills/ai-testflow` 专用 AI 组件原型，用于自动编排分析、生成、执行和报告流程。
4. 一个 `agents/ai-testflow-agent.*` 本地 Agent 原型，用于定义 AI 测试执行器的角色、输入、输出和行为约束。

这个项目的重点不是做一个复杂业务系统，而是把“从需求到缺陷”的完整测试链路跑通。

## 2. 为什么做这个项目

正式的一站式自动化测试插件通常需要接入公司内部系统，例如需求管理系统、接口平台、测试平台、CI 系统、Bug 系统。当前项目没有这些内部系统权限，所以先用一个本地可运行的 Demo 来模拟真实流程。

本项目选择登录注册功能作为业务载体，原因是：

1. 登录注册流程足够常见，理解成本低。
2. 注册、登录、登录态、退出登录都能形成明确测试点。
3. 用户名、密码、重复账号、错误密码等规则适合拆解测试用例。
4. 可以人工预埋一个业务规则缺陷，用于验证自动发现缺陷和生成 Bug 单的能力。

最终目标是证明下面这条链路是可落地的：

```text
PRD -> 需求拆解 -> 测试用例 -> 测试执行 -> 测试报告 -> Bug 单
```

## 3. 项目当前完成到什么程度

当前项目已经完成一版最小闭环：

1. React 前端页面已实现。
2. Flask 后端接口已实现。
3. SQLite 数据存储已实现。
4. 注册、登录、当前用户查询、退出登录流程已实现。
5. 预埋业务规则缺陷已实现。
6. 后端 pytest 自动化测试已实现。
7. PRD、需求规格、测试用例、执行记录、测试报告、Bug 单已输出。
8. AI 自动化测试插件最小原型设计方案已输出。
9. CLI 已实现 PRD 分析、需求结构化、测试用例清单生成、接口自动化测试脚本生成、pytest 执行、测试报告生成和 Bug 单生成。
10. Agent 原型已定义，用于把 CLI 和 Skill 封装成面向用户的一站式 AI 测试执行入口。

当前项目是“插件流程原型”，不是一个已经安装到浏览器、IDE 或测试平台里的插件成品。它的价值在于把插件要完成的工作拆清楚，并用本地 Demo 跑通证据链。

## 4. 项目目录怎么理解

项目根目录结构如下：

```text
AI-TestFlow/
  agents/
  ai_testflow/
  ai-testflow.yml
  ai-testflow-runs/
  backend/
  frontend/
  docs/
  skills/
  README.md
```

### 4.1 `backend/`

`backend/` 是 Flask 后端工程。

核心文件：

```text
backend/app.py
backend/requirements.txt
backend/tests/test_api.py
```

`backend/app.py` 提供接口、SQLite 初始化、密码哈希、登录态处理和统一响应结构。

`backend/tests/test_api.py` 提供接口自动化测试，用来验证注册、登录、当前用户查询、退出登录以及预埋缺陷。

### 4.2 `ai_testflow/`

`ai_testflow/` 是本项目的一站式自动化测试 CLI 原型。

它负责：

1. 读取 `ai-testflow.yml` 中声明的精确路径和命令。
2. 解析 `docs/prd.md`。
3. 生成运行态结构化需求。
4. 生成运行态测试用例清单。
5. 生成 pytest 接口自动化测试脚本。
6. 执行生成的测试脚本。
7. 汇总测试报告和 Bug 单。

### 4.3 `frontend/`

`frontend/` 是 React 前端工程。

核心文件：

```text
frontend/src/App.jsx
frontend/src/api.js
frontend/src/pages/RegisterPage.jsx
frontend/src/pages/LoginPage.jsx
frontend/src/pages/HomePage.jsx
frontend/src/styles.css
```

前端使用 React Router 管理页面路由，使用 Axios 调用后端接口，使用 Ant Design 实现表单、按钮、提示信息和页面组件。

### 4.4 `docs/`

`docs/` 是项目最核心的交付物目录。

它不是附属说明，而是这个项目用来证明“自动化测试全流程闭环”的主要证据。

核心文档：

| 文档 | 作用 |
| --- | --- |
| `docs/task-analysis-and-workflow.md` | 任务分析、阶段拆解、交付物规划 |
| `docs/prd.md` | 产品需求文档，定义系统目标和业务规则 |
| `docs/samples/requirement-spec.sample.md` | 需求规格样例 |
| `docs/samples/test-cases.sample.md` | 测试用例样例 |
| `docs/manual-test-execution.md` | 页面手工测试执行记录 |
| `docs/api-test-execution.md` | 接口自动化测试执行记录 |
| `docs/samples/test-report.sample.md` | 测试报告样例 |
| `docs/samples/bug-report.sample.md` | 标准 Bug 单样例 |
| `docs/plugin-prototype-design.md` | AI 自动化测试插件最小原型设计 |
| `docs/agent-prototype-design.md` | AI 自动化测试 Agent 原型设计 |
| `docs/project-introduction.md` | 项目整体介绍 |

### 4.5 `agents/`

`agents/` 是本项目的 Agent 原型目录。

核心文件：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

它定义 Agent 的角色、输入输出、调用命令、运行产物和行为约束。

### 4.6 `skills/ai-testflow/`

`skills/ai-testflow/` 是专用 AI 组件原型。

它的作用不是替代 CLI，而是告诉 AI 在本项目里应该如何读取配置、调用 CLI、检查运行产物、解释缺陷链路。

## 5. Demo 系统本身怎么运行

这个系统是前后端分离结构。

```text
React 前端
  -> Axios HTTP 请求
  -> Flask 后端接口
  -> SQLite users 表
```

前端地址：

```text
http://127.0.0.1:5173
```

后端地址：

```text
http://127.0.0.1:5000
```

### 5.1 前端页面

系统有三个主要页面：

| 页面 | 路径 | 作用 |
| --- | --- | --- |
| 注册页 | `/register` | 输入用户名、密码、确认密码，提交注册 |
| 登录页 | `/login` | 输入用户名和密码，提交登录 |
| 首页 | `/home` | 登录后展示当前登录用户名，并提供退出登录按钮 |

### 5.2 后端接口

后端提供四个接口：

| 接口 | 方法 | 作用 |
| --- | --- | --- |
| `/api/register` | POST | 注册用户 |
| `/api/login` | POST | 用户登录 |
| `/api/me` | GET | 获取当前登录用户信息 |
| `/api/logout` | POST | 退出登录 |

统一响应结构是：

```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "username": "testuser"
  }
}
```

失败响应结构是：

```json
{
  "success": false,
  "message": "用户名不能为空",
  "data": null
}
```

### 5.3 数据表

SQLite 中的用户表为 `users`。

字段如下：

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| `id` | INTEGER | 用户 ID |
| `username` | TEXT | 用户名 |
| `password_hash` | TEXT | 密码哈希 |
| `created_at` | TEXT | 创建时间 |

密码不是明文存储，而是通过 Werkzeug 的 `generate_password_hash` 生成哈希后保存。

## 6. 预埋 Bug 是什么

这个项目故意保留了一个业务规则类缺陷。

需求规则写在 PRD 里：

```text
PRD-FR-003 用户注册时，用户名长度必须大于等于 6 位。
```

需求规格中对应的规则是：

```text
REG-002 username 长度必须大于等于 6 位
```

验收标准中对应的是：

```text
AC-003 用户名长度小于 6 位时注册失败
```

测试用例中对应的是：

```text
TC-REG-003 用户名长度小于 6 位注册失败
```

Bug 单中对应的是：

```text
BUG-001 注册接口未校验用户名长度，短用户名可注册成功
```

完整追踪链如下：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

### 6.1 期望行为

当用户注册时输入：

```json
{
  "username": "abc",
  "password": "Password123",
  "confirm_password": "Password123"
}
```

系统应该返回注册失败：

```json
{
  "success": false,
  "message": "用户名长度不能少于6位",
  "data": null
}
```

### 6.2 实际行为

当前系统返回注册成功：

```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "username": "abc"
  }
}
```

这就是项目中用于验证测试流程的核心缺陷。

## 7. 为什么这个缺陷适合做原型验证

这个缺陷不是代码崩溃类问题，而是业务规则未实现问题。

这类问题很适合验证 AI 自动化测试能力，因为它要求 AI 做的不只是运行代码，还要理解需求：

1. PRD 里写了用户名长度规则。
2. 需求规格提取出了 `REG-002`。
3. 测试用例设计了 `TC-REG-003`。
4. 自动化测试或手工测试执行该用例。
5. 实际结果与期望结果不一致。
6. 测试报告记录风险。
7. Bug 单绑定需求、规则、验收标准和测试用例。

也就是说，AI 插件真正有价值的地方不是“发现接口返回 200”，而是识别“这个 200 与 PRD 期望不一致”。

## 8. AI 自动化测试插件在这个项目里怎么运作

插件的本质是一个流程编排器。它把散落在不同阶段的信息串起来，让每个阶段都有明确输入和输出。

### 8.1 第一步：读取 PRD

输入：

```text
docs/prd.md
```

插件读取 PRD，识别功能需求，例如：

```text
PRD-FR-003 用户名长度限制
```

读取结果不是只做摘要，而是要提取可测试规则：

```text
用户注册时，用户名长度必须大于等于 6 位。
```

### 8.2 第二步：结构化需求

输出：

```text
ai-testflow-runs/latest/requirements.json
```

Requirement Agent 把 PRD 分析结果整理成模块、规则、接口、页面和验收标准。

例如：

```text
PRD-FR-003 -> MOD-001 -> REG-002 -> AC-003
```

这一步的意义是把自然语言需求转成后续测试可以引用的结构化信息。

### 8.3 第三步：生成测试用例

输出：

```text
ai-testflow-runs/latest/test-cases.json
```

插件根据 PRD 分析和需求拆解结果生成运行态测试用例清单。

例如 `REG-002` 会生成：

```text
TC-REG-003 用户名长度小于 6 位注册失败
```

这条用例包含：

1. 关联需求：`PRD-FR-003`
2. 测试数据：`username=abc`, `password=Password123`, `confirm_password=Password123`
3. 期望结果：注册失败，提示 `用户名长度不能少于6位`

### 8.4 第四步：生成自动化测试脚本

输出：

```text
ai-testflow-runs/latest/generated_api_tests.py
```

插件根据测试用例编号和接口测试模板生成 pytest 脚本。

其中 `TC-REG-003` 会生成：

```text
test_generated_register_rejects_short_username
```

### 8.5 第五步：执行测试

接口自动化测试由 pytest 执行：

```bash
conda run -n AI-TestFlow python -m pytest -q ai-testflow-runs/latest/generated_api_tests.py
```

当前插件生成的自动化测试文件是：

```text
ai-testflow-runs/latest/generated_api_tests.py
```

测试内容覆盖：

1. 合法用户注册成功。
2. 用户名为空注册失败。
3. 密码为空注册失败。
4. 确认密码不一致注册失败。
5. 重复用户名注册失败。
6. 正确账号密码登录成功。
7. 密码错误登录失败。
8. 未注册用户登录失败。
9. 未登录访问 `/api/me` 失败。
10. 登录后访问 `/api/me` 成功。
11. 退出登录后登录态清除。
12. 短用户名注册失败，用于验证 PRD-FR-003 的业务规则。

### 8.6 第六步：对比期望结果和实际结果

对 `TC-REG-003` 来说：

期望结果：

```text
用户名长度小于 6 位时注册失败
```

实际结果：

```text
用户名长度小于 6 位时注册成功
```

插件判断这里存在需求实现偏差。

### 8.7 第七步：生成测试报告

输出：

```text
ai-testflow-runs/latest/generated-test-report.md
```

测试报告负责回答：

1. 本轮测了什么。
2. 测试环境是什么。
3. 多少用例通过。
4. 多少用例失败。
5. 发现了什么缺陷。
6. 当前系统能否上线。

当前报告结论是：

1. 登录注册主流程可运行。
2. 预埋缺陷可稳定复现。
3. 当前系统不满足正式上线标准，必须修复 `BUG-001` 后才能满足 `PRD-FR-003`。

### 8.8 第八步：生成 Bug 单

输出：

```text
ai-testflow-runs/latest/generated-bug-report.md
```

Bug 单不是只写一句“注册有问题”，而是完整描述：

1. Bug 编号：`BUG-001`
2. 标题：注册接口未校验用户名长度，短用户名可注册成功
3. 严重程度：Major
4. 优先级：P1
5. 关联需求：`PRD-FR-003`
6. 关联规则：`REG-002`
7. 关联验收标准：`AC-003`
8. 关联测试用例：`TC-REG-003`
9. 影响接口：`POST /api/register`
10. 影响页面：`/register`
11. 复现步骤
12. 期望结果
13. 实际结果
14. 修复建议

这就是“自动提 Bug”的最小形态。

## 9. Agent 在这个项目里怎么运作

Agent 是用户面对的一站式 AI 测试执行器。它不直接把所有逻辑写在对话里，而是调用已经稳定实现的 CLI，再读取运行产物输出结论。

当前 Agent 原型文件：

```text
agents/ai-testflow-agent.md
agents/ai-testflow-agent.yaml
```

Agent、Skill、CLI 的关系是：

```text
Agent：理解用户请求、编排流程、解释结果
Skill：告诉 AI 如何在本仓库执行流程
CLI：真正执行 PRD 分析、测试生成、pytest、报告和 Bug 单生成
```

Agent 的一次完整执行过程是：

```text
读取 agents/ai-testflow-agent.yaml
  -> 读取 ai-testflow.yml
  -> 读取 PRD、需求规格、测试用例、后端代码
  -> 调用 conda run -n AI-TestFlow python -m ai_testflow agent-run
  -> 读取 ai-testflow-runs/latest/ 运行产物
  -> 输出测试结论和 Bug 解释
```

这种设计的好处是：

1. Agent 负责 AI 理解和解释。
2. CLI 负责确定性执行，结果可复现。
3. pytest 负责真实测试，不靠口头判断。
4. JSON 和 Markdown 产物负责证据留存。

当前 Agent 识别到的缺陷实例是：

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

这条链来自 `defect-analysis.json` 中的缺陷列表，不是 Agent 只支持这一条链。

## 10. 从用户操作角度理解系统

你可以按下面流程体验系统：

### 10.1 正常注册登录流程

1. 打开 `http://127.0.0.1:5173/register`。
2. 输入用户名 `testuser`。
3. 输入密码 `Password123`。
4. 输入确认密码 `Password123`。
5. 点击注册。
6. 页面跳转到 `/login`。
7. 输入 `testuser` 和 `Password123`。
8. 点击登录。
9. 页面跳转到 `/home`。
10. 首页展示当前用户名。
11. 点击退出登录。
12. 页面返回 `/login`。

### 10.2 缺陷复现流程

1. 打开 `http://127.0.0.1:5173/register`。
2. 输入用户名 `abc`。
3. 输入密码 `Password123`。
4. 输入确认密码 `Password123`。
5. 点击注册。

按照 PRD，注册应该失败。

当前实际结果是注册成功，所以该流程对应 `BUG-001`。

## 11. 从开发角度理解系统

### 11.1 后端注册逻辑

注册接口在 `backend/app.py` 中，路径是：

```text
POST /api/register
```

它读取请求体中的：

```text
username
password
confirm_password
```

当前实现会校验：

1. `username` 不能为空。
2. `password` 不能为空。
3. `confirm_password` 必须与 `password` 一致。
4. `username` 不能重复。

当前实现故意没有校验：

```text
len(username) >= 6
```

这就是预埋缺陷。

### 11.2 后端登录逻辑

登录接口在 `backend/app.py` 中，路径是：

```text
POST /api/login
```

它读取：

```text
username
password
```

登录成功后写入 Flask session：

```text
session["username"]
```

之后 `/api/me` 通过 session 判断当前用户是否登录。

### 11.3 前端接口调用

前端接口配置在：

```text
frontend/src/api.js
```

Axios 配置了：

```text
baseURL: http://127.0.0.1:5000
withCredentials: true
```

`withCredentials: true` 的作用是让浏览器请求携带 session cookie，这样登录态才能在 `/api/login`、`/api/me`、`/api/logout` 之间保持。

## 12. 从测试角度理解系统

测试不是随便点页面，而是围绕需求编号来设计。

例如注册模块：

| 需求编号 | 测试用例 | 测试目的 |
| --- | --- | --- |
| PRD-FR-002 | TC-REG-002 | 验证用户名为空时注册失败 |
| PRD-FR-003 | TC-REG-003 | 验证用户名长度小于 6 位时注册失败 |
| PRD-FR-004 | TC-REG-004 | 验证密码为空时注册失败 |
| PRD-FR-005 | TC-REG-005 | 验证确认密码不一致时注册失败 |
| PRD-FR-006 | TC-REG-006 | 验证重复用户名注册失败 |
| PRD-FR-007 | TC-REG-001 | 验证合法用户注册成功 |

这样测试结果就能追溯回需求，而不是只记录“某个接口失败”。

## 13. 这个项目怎么用于简历表达

可以从三个层次介绍。

### 13.1 开发能力

可以说明：

1. 使用 React、Axios、React Router、Ant Design 搭建前端登录注册页面。
2. 使用 Flask、SQLite 实现注册、登录、当前用户查询和退出登录接口。
3. 使用 session 维护登录态。
4. 使用密码哈希存储用户密码。

### 13.2 测试能力

可以说明：

1. 基于 PRD 拆解需求规格。
2. 设计覆盖正常场景和异常场景的测试用例。
3. 使用 pytest 完成后端接口自动化测试。
4. 输出手工测试记录、接口测试记录、测试报告和 Bug 单。
5. 通过预埋缺陷验证测试闭环。

### 13.3 AI 插件设计能力

可以说明：

1. 设计 AI 自动化测试插件最小原型。
2. 将 PRD 解析、需求结构化、用例生成、测试执行、报告生成、Bug 单生成串成闭环。
3. 设计需求到 Bug 的追踪链路。
4. 用本地 Demo 验证插件流程，不依赖公司内部系统。

## 14. 面试时怎么讲这个项目

可以按下面顺序讲：

1. 项目背景：想验证 AI 自动化测试插件，但没有内部系统权限，所以用登录注册 Demo 做最小闭环。
2. 系统实现：前端 React，后端 Flask，数据库 SQLite。
3. 业务规则：用户名长度必须大于等于 6 位。
4. 预埋缺陷：后端注册接口没有实现该长度校验。
5. 测试设计：从 PRD 拆到需求规格，再生成测试用例 `TC-REG-003`。
6. 执行结果：短用户名 `abc` 注册成功，与期望不一致。
7. 缺陷输出：生成 `BUG-001`，绑定 `PRD-FR-003`、`REG-002`、`AC-003` 和 `TC-REG-003`。
8. 插件抽象：把这条链路抽象为 PRD 解析、需求结构化、用例生成、自动执行、报告生成、Bug 推送。

重点表达：

```text
这个项目不是只做了一个登录注册页面，而是用一个可控 Demo 跑通了 AI 自动化测试插件的最小闭环。
```

## 15. 后续可以继续做什么

当前项目已经完成最小闭环。后续可以继续增强：

1. 增加 PRD Markdown 自动解析脚本。
2. 增加结构化 JSON 作为插件内部中间产物。
3. 增加 Playwright 页面自动化测试。
4. 增加报告自动生成脚本。
5. 增加 Bug 单自动生成脚本。
6. 增加外部 Bug 系统推送适配层。
7. 把当前文档流程封装为一个命令行工具或 Web 插件原型。

## 16. 最重要的理解点

理解这个项目时，不要只看登录注册功能本身。登录注册只是载体。

真正的项目主线是：

```text
需求是否被正确理解
  -> 需求是否被拆成可测试规则
  -> 规则是否生成了测试用例
  -> 用例是否被执行
  -> 实际结果是否与期望一致
  -> 不一致时是否能自动生成 Bug 单
```

本项目通过 `PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001` 这条链路，把 AI 自动化测试插件的核心价值展示出来。
