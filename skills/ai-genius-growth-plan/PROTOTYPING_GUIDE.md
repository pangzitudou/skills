# HTML Prototyping Guide

## Principle

Quick HTML prototypes are AI-native requirement validation, not frontend implementation.

Use them to make abstract requirements visible before the team locks into Plan, Tasks, or implementation. The goal is not to become a UI specialist. The goal is to create a visible artifact that helps humans and AI judge flow, information architecture, states, and business acceptance.

## When to Prototype

Use an HTML prototype when the work involves:

- Screens, forms, dashboards, tables, or workflows.
- User operations and multi-step flows.
- Information architecture or page structure.
- Permission, empty, loading, error, disabled, or approval states.
- A stakeholder needs to see and react before implementation.
- The user is stuck in text descriptions and cannot tell whether the requirement is right.

Do not prototype when:

- The work is a purely invisible rule with no user flow, operation, or review surface.
- The requirement is still too vague for even a rough flow.
- The user is using prototype work to avoid deciding the business goal.

## Where It Fits

For new or visual work:

1. Brainstorm possible directions.
2. Grill Me to challenge decisions.
3. Generate a quick HTML prototype to validate visible flow and states.
4. Review the prototype and extract confirmed requirement decisions.
5. Decide whether to revise the prototype, write/update the project or feature SPEC, enter Plan, or run common SPEC impact analysis.

Prototype can feed a project or feature SPEC after human review. It can feed a company/common SPEC only when it reveals reusable rules. Do not turn every prototype detail into a shared standard.

## Prototype Rules

- Prototype for validation, not production.
- Prefer a single self-contained HTML file unless the execution context already has a better local pattern.
- Focus on flow, layout, information hierarchy, and states.
- Include realistic sample data.
- Include loading, empty, error, disabled, permission, approval, and pagination states when relevant.
- Avoid early analytics, performance tuning, animations, and visual polish unless they are core to the requirement.
- Do not lock a framework or stack unless it is a real constraint.
- Bring the prototype back for review before Plan.

## Execution Prompt

```text
请基于下面需求生成一个快速 HTML 原型，用于验证需求和交互流程。

注意：
- 这不是正式工程实现，不要选技术栈，不要拆工程任务。
- 优先做成单个自包含 HTML 文件。
- 重点验证流程、信息架构、页面结构、关键状态和业务验收点。
- 不要加入非核心的埋点、性能优化、复杂动画或过度视觉装饰。
- 不要把原型中的临时设计当成公司级通用 SPEC。

需求目标：[填写]
目标用户/使用者：[填写]
核心流程：[填写]
关键数据或样例：[填写]
权限/异常/空状态：[填写]
我现在不确定的地方：[填写]

请输出：
1. 原型覆盖的用户路径
2. HTML 原型代码
3. 原型中体现的关键状态
4. 仍然需要业务方确认的问题
5. 哪些内容不应该在此阶段加入
```

## Prototype Review Prompt

```text
请基于这个 prototype 做一次原型复盘，不要写技术方案，不要拆任务，不要进入实现。

原型材料：
[粘贴链接/截图/HTML/说明]

请输出：
1. 原型覆盖的核心用户路径
2. 已经被原型验证成立的需求点
3. 原型暴露出的未确认问题
4. 可以删除或延后的非核心内容
5. 需要补充验证的关键状态：loading、empty、error、disabled、permission、approval、pagination 等
6. 是否存在技术偏好、历史实现或视觉装饰干扰需求判断
7. 哪些结论可以进入 SPEC
8. 哪些内容还不能进入 Plan
9. 是否需要做公司级/公共 SPEC 影响分析；如果需要，只说明影响领域和原因，不要直接写完整公共规范

请特别注意：
以需求为中心，不要被技术偏好或历史实现绑架。
做加法前，先做减法。
这不是实现验收，而是需求和流程验证。
```

## Review Checklist

The prototype is useful when:

- The core user path is visible.
- The user can tell what happens first, next, and last.
- Key information hierarchy is clear.
- Important states are represented.
- It exposes open questions or hidden assumptions.
- Stakeholders can accept, reject, or revise the flow.
- It does not pretend to be production implementation.
- It produces clear input for SPEC or Plan.

Go back when:

- The prototype only looks nice but does not validate the requirement.
- It locks a framework or architecture without a real constraint.
- It skips important states.
- It hides unclear business decisions behind UI decoration.
- It expands scope before the core path is accepted.
- It tries to turn one-off prototype choices into company/common SPEC rules without review.
