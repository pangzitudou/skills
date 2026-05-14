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

## Standard Map

`comm/README.md` should work as the routing table for humans and AI.

Use this minimum table:

| Group | Document | Solves | Key artifacts |
| --- | --- | --- | --- |
| Identity and security | `WECOM_LOGIN_AND_PERM_SPEC.md` | Login, user identity alignment, permission model | User tables, permission UI skeleton |
| Audit and logging | `AUDIT_AND_LOGGING_SPEC.md` | Traceable business audit and API logs | `audit_log`, `write_audit` |
| External API | `EXTERNAL_OPEN_API_PLATFORM_STANDARD.md` | Unified external API shape, auth, keys, encrypted storage, admin UI | `/open/v1/*`, client docs, Swagger |
| Integration | `*_INTEGRATION.md` | Third-party identity, API, and message flows | identity maps, API keys, robot ids |
| UI and experience | `INTERNAL_UI_DESIGN_SPEC.md` | Internal system visual and interaction consistency | `tokens.css`, `app.css`, base layout |
| Engineering docs | `SYSTEM_DOCUMENTATION_STANDARD.md` | Repository docs, README roles, API/doc ownership | docs structure, responsibility matrix |
| Performance and operations | `PERFORMANCE_TESTING_AND_OPTIMIZATION_STANDARD.md` | Performance testing, capacity, regression, release checks | test plan, report, optimization log |
| Security scanning | `SECURITY_SCANNING_AND_REMEDIATION_STANDARD.md` | Pre-release scan, risk grading, remediation and retest | scan plan, report, fix log, blockers |
| Tech stack and access layer | `WEB_SERVICE_TECH_STACK_STANDARD.md`, `BFF_ACCESS_LAYER_STANDARD.md` | Default stack and client access boundary | `.env.example`, migrations, BFF APIs, DTO validation |

The coach should treat this as a pattern, not a required taxonomy. Add a group only when it solves repeated drift.

## Documentation Meta-Standard

A mature SPEC system should include `SYSTEM_DOCUMENTATION_STANDARD.md`. It defines how project documentation is written and prevents duplicate, stale, or hidden knowledge.

Recommended implementation steps:

1. Decide the official docs root. New projects should usually use `docs/`.
2. Trim root `README.md` to project positioning, local run command, test command, optional directory sketch, and link to the docs center.
3. Create `docs/README.md` as the docs center with role-based reading order, document responsibility matrix, and maintenance rules.
4. Register adopted `comm` specs in `README.md`, `AGENTS.md`, or `CLAUDE.md`.
5. Choose the authoritative API document. API fields, error codes, and auth rules should live in one place.
6. Create special docs only when needed: permission, audit, masking, performance, security, deployment, master-data integration.
7. Before release, check dead links, duplicated tables, API sync, and valid project entrypoint references.

README responsibility split:

| File | Readers | Must contain |
| --- | --- | --- |
| Root `README.md` | First-time cloners, CI, people who only glance | One-line positioning, local run command, test command, optional directory sketch, docs center link |
| `docs/README.md` | Developers, testers, integrators, product readers | Role-based reading order, document responsibility matrix, maintenance rules |
| `AGENTS.md` / `CLAUDE.md` | AI execution threads | Project overview, adopted `comm` specs, project-specific constraints, verification commands |

Common project docs:

| Purpose | Suggested names |
| --- | --- |
| System overview | `SYSTEM_UNDERSTANDING.md`, `OVERVIEW.md` |
| Development | `DEVELOPMENT.md`, `DEVELOPMENT_GUIDE.md` |
| External integration | `INTEGRATION.md`, `INTEGRATION_GUIDE.md` |
| HTTP/Open API contract | `API.md`, `API_SPEC_FINAL.md` |
| Testing and acceptance | `TESTING.md`, `FULL_TEST_GUIDE.md` |
| Deployment and operations | `DEPLOYMENT.md` |
| Product/design master | `SYSTEM_DESIGN*.md`, prototype HTML, SQL sketches |
| Permission and security | `PERMISSION_MATRIX.md`, `*_RULES.md`, `SECURITY_HARDENING.md` |

Minimum docs by system type:

- External API: root README, `docs/README`, integration guide, API contract, development guide, testing guide.
- Master data or many downstream consumers: the above plus master-data docs, consumer list, alignment notes.
- Compliance or sensitive data: the above plus security hardening, masking/audit rules, permission matrix.
- Internal admin only: integration guide can often be omitted; internal APIs should still have one authoritative contract when routes matter.

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
7. Developer implementation steps: the shortest path humans and AI should follow.
8. Key artifacts: files, tables, tokens, APIs, templates, reports, prompts, or screenshots controlled by the spec.
9. Rules: concrete reusable rules, not vague principles.
10. Examples: small examples that show the expected pattern.
11. Don't list: things humans and AI must not do.
12. Review checklist: how to judge whether an output follows the spec.
13. AI upgrade prompt: a copyable prompt for execution threads to apply the spec to a project.
14. Version and change log: what changed and why.

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
- It has no key artifacts, so AI cannot tell what to modify or verify.
- It lacks an AI upgrade prompt, so every execution thread reinvents how to apply it.
- It is readable by humans but gives AI no routing, files, artifacts, or prompt.
- It is useful to AI but unreadable or unreviewable by humans.

## Hard Don'ts for SPEC Systems

- Do not duplicate the same long table in root `README.md` and `docs/README.md`.
- Do not maintain the same API field table in multiple documents.
- Do not change an interface without updating the authoritative API document.
- Do not keep long-lived "temporary notes" beside official docs.
- Do not leave key development constraints only in chat history.
- Do not let `AGENTS.md`, `CLAUDE.md`, or `README.md` reference missing `comm` paths.
- Do not create a new SPEC when an existing standard can be extended cleanly.
- Do not add performance, security scanning, or operational gates before the core function is accepted unless they are real constraints.

## Build a SPEC System Prompt

```text
请帮我为团队建立一个最小可用的 comm/ SPEC 规范体系。

注意：
- SPEC 是团队共享规范文档体系，不是单次需求 PRD。
- 目标是让人能照着做，让 AI 能作为上下文执行。
- 先做最小体系，不要一次性设计过多规范。

团队/项目背景：
[填写]

当前最容易漂移的问题：
[例如 UI、API、文档、权限、审计、测试、部署]

已有项目入口文件：
[AGENTS.md / CLAUDE.md / README.md 情况]

请输出：
1. 建议的 comm/README.md 标准地图，字段包括：分组、文档名、解决什么、关键产物
2. 第一批必须建立的 3-5 份 SPEC
3. 哪些规范暂时不要建，为什么
4. SYSTEM_DOCUMENTATION_STANDARD.md 应该管哪些规则
5. 项目 AGENTS.md / CLAUDE.md / README.md 应该如何引用 comm/
6. 最小落地步骤
7. Don't 清单
8. 后续让执行线程生成每份 SPEC 草稿的 prompt
```

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
8. comm/README.md 标准地图是否需要更新
9. 根 README / docs/README / API 权威文档是否受影响
10. 建议的最小变更范围
11. 下一步用于生成 SPEC diff 的 prompt

请特别自检：
- 有没有把单次需求写成通用规范？
- 有没有把技术偏好或历史实现固化成规范？
- 有没有先做减法，去掉不必要规则？
- 有没有造成 README、API 文档或规范之间的重复维护？
- AGENTS.md / CLAUDE.md / README.md 引用路径是否有效？
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
