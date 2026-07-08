# AI-TestFlow Traceability

Use this file when explaining defect mappings discovered by the AI-TestFlow skill.

## Current Demo Defect Example

```text
PRD-FR-003 -> REG-002 -> AC-003 -> TC-REG-003 -> BUG-001
```

This is the current Demo's discovered defect, not the only chain the one-stop workflow can represent.

## Meaning

| ID | Meaning |
| --- | --- |
| `PRD-FR-003` | 用户注册时，用户名长度必须大于等于 6 位 |
| `REG-002` | `username` 长度必须大于等于 6 位 |
| `AC-003` | 用户名长度小于 6 位时注册失败 |
| `TC-REG-003` | 用户名长度小于 6 位注册失败 |
| `BUG-001` | 注册接口未校验用户名长度，短用户名可注册成功 |

## Expected Generated Test Behavior

The generated test `test_generated_register_rejects_short_username` sends:

```json
{
  "username": "abc",
  "password": "Password123",
  "confirm_password": "Password123"
}
```

Expected behavior:

```text
HTTP 400
用户名长度不能少于6位
```

Actual behavior in the intentional Demo defect:

```text
HTTP 200
注册成功
```

## Reporting Sentence

Use this concise explanation for the current Demo defect:

```text
AI-TestFlow 检验确认：PRD-FR-003 要求用户名长度必须大于等于 6 位，但后端注册接口未实现 REG-002；TC-REG-003 因实际返回 HTTP 200 而失败，该失败形成 BUG-001。
```
