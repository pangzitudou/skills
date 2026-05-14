# SPEC / comm Guide

## What SPEC Means

SPEC is the team's shared Specification Documents System.

It is not:

- A built-in AI tool skill.
- A one-off PRD.
- The core stage of the delivery flow.
- A place to freeze every prototype decision.

It is:

- A reusable constraint and context system.
- Usually stored in a shared `comm/` directory.
- Referenced by each project through `AGENTS.md`, `CLAUDE.md`, or `README.md`.
- Written for both humans and AI: humans can follow it directly; AI can load it as context and apply it to new systems.

Core idea:

> This document is for both humans and AI: humans can copy the rule to keep work consistent; AI can use it as context to transform or build new systems.

## Typical Structure

```text
comm/
  README.md                              # standard map and repository purpose
  SYSTEM_DOCUMENTATION_STANDARD.md       # meta-standard for writing docs
  INTERNAL_UI_DESIGN_SPEC.md             # UI and interaction standard
  EXTERNAL_OPEN_API_PLATFORM_STANDARD.md # external API standard
  WEB_SERVICE_TECH_STACK_STANDARD.md     # technology and engineering standard
  ...

project/
  AGENTS.md / CLAUDE.md / README.md      # AI entrypoint: references comm specs and project rules
  docs/                                  # project docs maintained by AI and humans
  ...
```

The categories above are examples, not law. The important pattern is: shared reusable rules live in `comm/`; project entrypoints reference them and add local context.

## When to Touch SPEC

Use SPEC work when:

- A rule should apply across many projects or repeated future tasks.
- AI keeps drifting because a shared constraint is missing.
- A prototype exposes reusable UI, workflow, state, permission, QA, API, docs, or deployment rules.
- A project needs an `AGENTS.md`, `CLAUDE.md`, or `README.md` entrypoint to reference existing `comm/` specs.
- A completed implementation changes the standard the team should reuse next time.
- The team needs a routing map that tells AI which standard to load for each domain.

Do not touch SPEC when:

- The question is only a single requirement.
- The prototype has not been reviewed by humans.
- The decision is a one-off client/project exception.
- The rule is only a personal technology preference.
- The current implementation shape is being mistaken for a standard.
- The user is trying to avoid clarifying the requirement by writing a document.

## Coach Behavior

When users ask for "SPEC", first clarify what they mean:

- Requirement artifact: a PRD, issue, brief, acceptance note, or project-native requirement document.
- SPEC system update: a reusable `comm/` standard or project entrypoint reference.

If they mean a SPEC system update, do not write a full document immediately. Guide this order:

1. Identify the affected domain: UI, workflow, API, permission, testing, docs, deployment, data, security, or other.
2. Inspect or ask for the existing `comm/` standard map.
3. Decide whether to update an existing standard, add a new standard, or only update a project entrypoint.
4. Separate reusable rules from one-off project details.
5. Propose the minimal diff.
6. Review for duplication, false constraints, and usability by both humans and AI.

## SPEC Document Shape

A useful `comm/` SPEC should usually include:

1. Title and purpose: what inconsistency or drift this standard prevents.
2. Audience: how humans use it and how AI uses it.
3. Scope: where it applies.
4. Non-scope: where it must not be applied.
5. Source of truth: related files, APIs, modules, examples, or owner documents.
6. Relationship to other specs: which standards should be loaded before or after it.
7. Rules: concrete reusable rules, not vague principles.
8. Examples: small examples that show the expected pattern.
9. Don't list: things humans and AI must not do.
10. Review checklist: how to judge whether an output follows the spec.
11. AI usage prompt: a copyable prompt for execution threads.
12. Version and change log: what changed and why.

Keep it constraint-light. A good SPEC removes false constraints and keeps only rules that protect consistency, safety, maintainability, or business acceptance.

## Good SPEC Qualities

- Reusable: it applies beyond one request.
- Requirement-rooted: it explains what problem the standard prevents.
- Constraint-light: it avoids freezing personal preference or historical accident.
- Operational: humans know what to do, and AI knows what context to load.
- Reviewable: it contains concrete checks.
- Anti-drift: it points to source artifacts and project entrypoints.
- Maintained: it has an update rule and change log.

## Bad SPEC Smells

- It is really a PRD wearing a SPEC title.
- It starts from a favored technology instead of a requirement.
- It preserves current implementation shape without justification.
- It turns a prototype's temporary UI into a permanent standard too early.
- It adds many rules before removing false constraints.
- It has principles but no checks.
- It is readable by humans but gives AI no routing, files, artifacts, or prompt.
- It is useful to AI but unreadable or unreviewable by humans.

## SPEC Impact Analysis Prompt

```text
请基于下面材料做一次 SPEC 规范体系影响分析。

注意：
- SPEC 不是单次需求 PRD。
- SPEC 是团队共享的规范文档体系，通常位于 comm/ 目录。
- 项目通过 AGENTS.md / CLAUDE.md / README.md 引用 comm/ 中的规范。
- 先不要直接写完整规范文档，不要写技术方案，不要拆任务。
- 目标是判断哪些内容值得沉淀为通用规范，哪些只是本次特例。

输入材料：
1. prototype / PRD / 实现结果：[粘贴链接、截图、HTML、说明或摘要]
2. 当前项目背景：[项目名称、业务场景、目标用户]
3. 现有 comm/ 规范目录：[粘贴清单，或让 AI 读取]
4. 当前项目 AGENTS.md / CLAUDE.md / README.md：[粘贴或让 AI 读取]
5. 已确认的结论：[填写]
6. 未确认的问题：[填写]

请输出：
1. 涉及的规范领域：UI / 流程 / 接口 / 权限 / 测试 / 文档 / 部署 / 数据 / 安全 / 其他
2. 应该更新哪些已有 SPEC
3. 是否需要新增 SPEC，为什么
4. 可沉淀为通用规范的规则
5. 不应该沉淀的本次特例
6. 与现有 comm/ 规范是否冲突或重复
7. AGENTS.md / CLAUDE.md / README.md 是否需要补充引用
8. 建议的最小变更范围
9. 下一步用于生成 SPEC diff 的 prompt

请特别自检：
- 有没有把单次需求写成通用规范？
- 有没有把技术偏好或历史实现固化成规范？
- 有没有先做减法，去掉不必要规则？
- 输出是否同时方便人照着做，也方便 AI 当上下文使用？
```

## Minimal SPEC Diff Prompt

```text
请基于下面的 SPEC 影响分析，生成最小规范变更建议。

注意：
- 只输出需要更新的文档、章节和建议 diff。
- 不要重写整个 comm/。
- 不要加入未验证的规则。
- 不要把本次需求特例沉淀成通用规范。

SPEC 影响分析：
[粘贴]

现有相关规范：
[粘贴或让 AI 读取]

请输出：
1. 需要修改的文件
2. 每个文件的修改目的
3. 建议新增/修改/删除的条目
4. 与其他规范的关系
5. AGENTS.md / CLAUDE.md / README.md 是否需要更新
6. Review checklist
```
