# Methodology Gaps

Use this when the user asks something not covered by the bundled methodology.

## Principle

The methodology is strict. If it does not cover the question, do not improvise generic advice.

Instead, turn the question into a methodology gap that can improve the system.

## Response Pattern

```text
当前方法论没有覆盖这个问题，所以我不临时发挥。

方法论缺口：
- 用户问题：[原问题]
- 当前无法回答的原因：[缺少哪类原则、流程、检查清单或案例]
- 建议补充位置：[REFERENCE / SPEC_GUIDE / PROTOTYPING_GUIDE / HUMAN_QA_GUIDE / CHECKLISTS / EXAMPLES / ANTI_PATTERNS / ADOPTION_GUIDE]
- 建议补充内容：[一两句话描述要补什么]

下一步建议：
请先把这个问题记录到方法论缺口列表。等方法论补充后，我再基于新规则回答。
```

## Gap Categories

- Missing stage rule: the methodology does not say which phase the user is in.
- Missing checklist: the methodology has a principle but no review method.
- Missing role example: the situation is non-development and lacks a role-specific example.
- Missing risk boundary: the methodology does not say where human approval is required.
- Missing SPEC system pattern: the user needs a `comm/` standard or project entrypoint pattern not yet described.
- Missing anti-pattern: a repeated bad habit is visible but not yet named.
