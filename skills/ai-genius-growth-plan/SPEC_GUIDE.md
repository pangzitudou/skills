# SPEC Guide

## What a SPEC Is

A SPEC is a shared context interface between humans and AI.

It is not just a requirement document. It is the place where the team records the target, constraints, execution order, artifacts, and review rules so that humans and AI can work from the same source of truth.

Good SPECs reduce repeated explanation, prevent local drift, and stop AI from redesigning privately.

## When to Create a SPEC

Create a SPEC when:

- Work starts from zero to one.
- The project affects multiple modules, roles, systems, or agents.
- The team needs consistent behavior across many projects.
- AI will repeatedly generate or modify related artifacts.
- The cost of misunderstanding is high.

Do not create a heavy SPEC for every tiny change. Small follow-up work can use a lighter target, boundary, and acceptance note.

## Core Structure

Use this structure unless the domain has a better existing standard:

1. Title and purpose: what this SPEC standardizes.
2. Audience: who uses it, including humans and AI.
3. Source of truth: which project, module, files, APIs, or docs it applies to.
4. Update rule: how to change the SPEC and how AI should apply the change.
5. Execution steps: the recommended order for humans or AI to follow.
6. Quick index: sections or related standards, grouped by domain.
7. Principles: the few rules that beat all details.
8. Tokens or shared primitives: names, data structures, styles, APIs, permissions, or other reusable units.
9. Architecture or layout rules: the stable skeleton.
10. Component or module rules: repeated patterns and allowed variants.
11. Interaction and state rules: loading, empty, error, permission, disabled, toast, pagination, and other states.
12. Business module structure: how domain pages, flows, or workflows should be organized.
13. Review checklist: how to decide whether output is acceptable.
14. Don't list: what AI and humans must not do.
15. AI upgrade prompt: a copyable prompt for applying the SPEC.
16. Version and change log: what changed and why.

## Standard Map Pattern

For large teams, keep a standard map that lists each standard document and what it solves.

Use columns like:

- Group: API, integration, UI, engineering docs, performance, security, tech stack.
- Document: the standard file.
- Solves: the problem this standard prevents.
- Key artifacts: files, templates, reports, APIs, scripts, or prompts controlled by the standard.

This gives AI a routing table: when a task touches UI, load the UI standard; when it touches security, load the security standard; when it touches integration, load the integration standard.

## Good SPEC Qualities

- Requirement-first: it explains why the standard exists before describing how.
- Constraint-light: it removes false constraints and keeps only real constraints.
- Operational: it tells users and AI what to do next.
- Reviewable: it contains concrete checks, not just ideals.
- Anti-drift: it says which artifacts must stay consistent.
- Copyable: it includes prompts users can give to execution threads.
- Maintained: it has an update rule and change log.

## Bad SPEC Smells

- It starts from a favored technology instead of a requirement.
- It describes implementation details without acceptance rules.
- It has many principles but no execution steps.
- It has examples but no Don't list.
- It is useful to humans but gives AI no file, module, or artifact context.
- It is useful to AI but unreadable to humans.
- It creates new constraints before removing false constraints.

## Coach Behavior

When users ask for a SPEC, do not write the complete SPEC by default.

Instead:

1. Identify the domain and scope.
2. Ask whether this needs a full SPEC or a light checklist.
3. Provide the structure above.
4. Give a prompt for an execution thread to draft the SPEC.
5. Review the drafted SPEC with the checklist.

If the user explicitly asks for a template, provide a blank template with fill-in fields.

## Drafting Prompt

```text
请基于下面的背景起草一份 SPEC。

先不要给实现方案，也不要开始拆任务。
这份 SPEC 的目标是成为人和 AI 的共同上下文接口：人能照着执行，AI 能根据它加载上下文、遵守约束、生成或修改产物。

背景：[填写]
适用范围：[填写]
涉及系统/模块/文档/文件：[填写]
真实约束：[填写]
不确定点：[填写]

请按以下结构输出：
1. 标题和目的
2. 使用对象：人和 AI 分别如何使用
3. 适用范围和来源上下文
4. 更新规则
5. 执行步骤
6. 快速索引或相关标准表
7. 核心原则
8. 共享原语或关键产物
9. 架构/布局/流程规则
10. 组件/模块/场景规则
11. 交互、状态、异常或风险规则
12. 检查清单
13. Don't 清单
14. AI 升级提示词
15. 版本与变更记录

特别检查：
- 有没有被个人技术偏好、既有实现或历史惯性污染？
- 有没有先做减法，去掉伪约束？
- 有没有明确什么情况下可以进入 Plan？
```

