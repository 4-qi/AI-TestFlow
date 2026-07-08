# 登录注册 Demo 系统测试用例

## 1. 测试范围

本测试用例覆盖登录注册 Demo 的核心功能：

1. 注册页面。
2. 注册接口。
3. 登录页面。
4. 登录接口。
5. 首页登录态展示。
6. 退出登录。

## 2. 测试用例列表

| 用例编号 | 关联需求 | 标题 | 前置条件 | 测试数据 | 期望结果 | 优先级 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-REG-001 | PRD-FR-007 | 合法用户注册成功 | 用户名未存在 | `username=testuser`, `password=Password123`, `confirm_password=Password123` | 注册成功，返回用户名 `testuser` | P0 |
| TC-REG-002 | PRD-FR-002 | 用户名为空注册失败 | 无 | `username=`, `password=Password123`, `confirm_password=Password123` | 注册失败，提示 `用户名不能为空` | P0 |
| TC-REG-003 | PRD-FR-003 | 用户名长度小于 6 位注册失败 | 用户名未存在 | `username=abc`, `password=Password123`, `confirm_password=Password123` | 注册失败，提示 `用户名长度不能少于6位` | P0 |
| TC-REG-004 | PRD-FR-004 | 密码为空注册失败 | 无 | `username=testuser`, `password=`, `confirm_password=` | 注册失败，提示 `密码不能为空` | P0 |
| TC-REG-005 | PRD-FR-005 | 确认密码不一致注册失败 | 无 | `username=testuser`, `password=Password123`, `confirm_password=Password456` | 注册失败，提示 `两次输入的密码不一致` | P0 |
| TC-REG-006 | PRD-FR-006 | 重复用户名注册失败 | `testuser` 已注册 | `username=testuser`, `password=Password123`, `confirm_password=Password123` | 注册失败，提示 `用户名已存在` | P0 |
| TC-LOGIN-001 | PRD-FR-011 | 正确账号密码登录成功 | `testuser` 已注册 | `username=testuser`, `password=Password123` | 登录成功，返回用户名 `testuser` | P0 |
| TC-LOGIN-002 | PRD-FR-010 | 密码错误登录失败 | `testuser` 已注册 | `username=testuser`, `password=WrongPassword` | 登录失败，提示 `用户名或密码错误` | P0 |
| TC-LOGIN-003 | PRD-FR-009 | 未注册用户登录失败 | 用户名未注册 | `username=missinguser`, `password=Password123` | 登录失败，提示 `用户名或密码错误` | P0 |
| TC-ME-001 | PRD-FR-013 | 未登录访问当前用户失败 | 未登录 | 无 | 获取失败，提示 `用户未登录` | P1 |
| TC-ME-002 | PRD-FR-013 | 登录后获取当前用户成功 | `testuser` 已登录 | 无 | 获取成功，返回用户名 `testuser` | P1 |
| TC-LOGOUT-001 | PRD-FR-014 | 退出登录后清除登录态 | `testuser` 已登录 | 无 | 退出成功，再访问当前用户接口提示 `用户未登录` | P1 |

## 3. 缺陷触发用例

| 项目 | 内容 |
| --- | --- |
| 用例编号 | TC-REG-003 |
| 关联需求 | PRD-FR-003 |
| 关联规则 | REG-002 |
| 期望结果 | 用户名长度小于 6 位注册失败 |
| 实际结果 | 当前后端注册接口未校验用户名长度，`username=abc` 可注册成功 |
| 缺陷单 | BUG-001 |

