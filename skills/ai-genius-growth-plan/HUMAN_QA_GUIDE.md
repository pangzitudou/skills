# Human QA Guide

## Principle

Human QA in AI-native work is not old-style manual testing. The human acts as AI's hands, feet, eyes, and business judgment.

AI should design the QA plan, list the steps, explain what to observe, and repair based on feedback. The human should operate in the real environment, observe real behavior, capture evidence, and decide whether the business outcome is acceptable.

## Where It Fits

Use this after implementation and before final acceptance.

The loop is:

1. AI generates a QA plan.
2. Human executes the plan in the real environment.
3. Human reports evidence and failures.
4. AI fixes issues and updates tests or docs.
5. Human re-runs focused checks.
6. Human gives business acceptance or sends it back.

## Responsibility Boundary

AI should:

- Read the requirement, SPEC, Plan, implementation notes, and known risks.
- Generate a step-by-step QA checklist.
- Explain what to click, enter, observe, screenshot, or record.
- Define pass/fail criteria for each step.
- Ask for logs, screenshots, URLs, test accounts, or environment details when needed.
- Fix issues based on structured feedback.
- Update automated tests or docs when the issue reveals a gap.

Human should:

- Use the real or staging environment.
- Follow the QA checklist.
- Capture screenshots, logs, URLs, timestamps, and exact data when useful.
- Describe actual vs expected behavior.
- Decide whether the result satisfies the business goal.
- Escalate high-risk, compliance, payment, data, permission, or customer-impact issues.

Human should not:

- Invent the whole QA plan from scratch when AI can draft it.
- Click around randomly and call it tested.
- Start debugging code manually before feeding evidence back to AI.
- Accept the result only because AI says tests passed.

## QA Plan Prompt

```text
请基于下面需求和实现结果生成一份人工 QA 清单。

我会作为你的手、脚和眼睛在真实环境中操作。
请告诉我每一步要点哪里、输入什么、观察什么、什么算通过、失败时要记录什么。

需求目标：[填写]
验收标准：[填写]
实现说明或变更摘要：[填写]
测试环境/地址：[填写]
已知风险或重点关注点：[填写]

请输出：
1. QA 范围和不测范围
2. 前置条件和测试数据
3. Happy path 操作步骤
4. 关键异常路径
5. 权限、空状态、错误状态、禁用状态、加载状态检查
6. 每一步的通过/失败标准
7. 失败时需要我提供的证据
8. 是否可以进入业务验收的判断标准
```

## Human Feedback Template

```text
QA 反馈：

测试环境/地址：
测试账号/角色：
操作步骤：
实际结果：
期望结果：
截图/录屏/日志：
使用的数据：
发生时间：
是否可复现：
是否阻塞业务验收：
我的业务判断：
```

## Acceptance Layers

- AI automated checks: unit tests, basic logic, static checks, self-review.
- AI plus tools: smoke-level browser or E2E checks.
- Human QA: real environment, real operations, evidence capture, complex interaction, state verification.
- Business acceptance: whether the outcome achieves the business goal and can be shipped.

## Human QA Checklist

Before accepting:

- AI produced a QA plan instead of only saying tests passed.
- Happy path was checked in the real or staging environment.
- Important states were checked: loading, empty, error, disabled, permission, approval, pagination, or data edge cases when relevant.
- The human captured enough evidence for any failure.
- AI fixed or explained failures and updated tests/docs if needed.
- The final decision was based on business outcome, not code appearance.

