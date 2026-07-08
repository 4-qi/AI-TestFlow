# BUG-001 注册接口未校验用户名长度

| 字段 | 内容 |
| --- | --- |
| Bug 编号 | `BUG-001` |
| 关联需求 | `PRD-FR-003` |
| 关联规则 | `REG-002` |
| 关联验收标准 | `AC-003` |
| 关联测试用例 | `TC-REG-003` |
| 自动化失败用例 | `test_register_rejects_short_username_by_requirement` |
| pytest exit code | `1` |

## 1. 期望结果

用户名长度小于 6 位时注册失败，HTTP 400。

## 2. 实际结果

用户名长度小于 6 位时注册成功，HTTP 200。

## 3. CLI 检验结论

`python -m ai_testflow run` 已完成执行，插件本身执行成功，并发现 `BUG-001`。该缺陷来自真实自动化测试失败，不是测试脚本通过后人工标记的问题。
