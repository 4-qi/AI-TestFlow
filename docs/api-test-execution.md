# 接口自动化测试执行记录

## 1. 执行环境

| 项目 | 内容 |
| --- | --- |
| 执行日期 | 2026-07-07 |
| Python 环境 | Conda `AI-TestFlow` |
| Python 版本 | 3.10.20 |
| 测试框架 | pytest 8.2.2 |
| 被测模块 | Flask 后端接口 |
| 测试命令 | `conda run -n AI-TestFlow python -m pytest -q ai-testflow-runs/latest/generated_api_tests.py` |

## 2. 执行结果摘要

| 项目 | 数量 |
| --- | --- |
| 自动化用例总数 | 12 |
| 执行通过 | 11 |
| 执行失败 | 1 |
| 发现缺陷 | 1 |

说明：

自动化测试中的短用户名相关用例为 `test_generated_register_rejects_short_username`。该用例由 CLI 根据测试用例清单生成，按 PRD-FR-003 和 REG-002 断言短用户名应注册失败。当前系统实际返回注册成功，因此该用例失败，并形成 BUG-001 的真实测试证据。

## 3. 命令输出

```text
..F.........                                                             [100%]
FAILED ai-testflow-runs/latest/generated_api_tests.py::test_generated_register_rejects_short_username
1 failed, 11 passed in 0.86s
```

## 4. 接口执行明细

| 测试编号 | 关联用例 | 接口 | 请求方法 | 执行结果 | 说明 |
| --- | --- | --- | --- | --- | --- |
| API-EXEC-001 | TC-REG-001 | `/api/register` | POST | 通过 | 合法用户注册成功 |
| API-EXEC-002 | TC-REG-002 | `/api/register` | POST | 通过 | 空用户名被拒绝 |
| API-EXEC-003 | TC-REG-004 | `/api/register` | POST | 通过 | 空密码被拒绝 |
| API-EXEC-004 | TC-REG-005 | `/api/register` | POST | 通过 | 两次密码不一致被拒绝 |
| API-EXEC-005 | TC-REG-006 | `/api/register` | POST | 通过 | 重复用户名被拒绝 |
| API-EXEC-006 | TC-REG-003 | `/api/register` | POST | 失败 | 按需求短用户名应被拒绝，当前实现未拒绝 |
| API-EXEC-007 | TC-LOGIN-001 | `/api/login` | POST | 通过 | 正确账号密码登录成功 |
| API-EXEC-008 | TC-LOGIN-002 | `/api/login` | POST | 通过 | 错误密码登录失败 |
| API-EXEC-009 | TC-LOGIN-003 | `/api/login` | POST | 通过 | 未注册用户登录失败 |
| API-EXEC-010 | TC-ME-001 | `/api/me` | GET | 通过 | 未登录访问当前用户失败 |
| API-EXEC-011 | TC-ME-002 | `/api/me` | GET | 通过 | 登录后可获取当前用户 |
| API-EXEC-012 | TC-LOGOUT-001 | `/api/logout` | POST | 通过 | 退出登录后登录态清除 |

## 5. 缺陷结论

| 项目 | 内容 |
| --- | --- |
| 缺陷编号 | BUG-001 |
| 关联需求 | PRD-FR-003 |
| 关联用例 | TC-REG-003 |
| 请求数据 | `username=abc`, `password=Password123`, `confirm_password=Password123` |
| 期望结果 | 注册失败，提示 `用户名长度不能少于6位` |
| 实际结果 | 注册成功，提示 `注册成功` |
