# AI Native Methodology Coach Design

## Goal

Create a shareable skill that helps teammates understand and apply the internal AI-native methodology inside Codex, Claude Code, or similar agent environments.

The skill is a coach, not an executor. It helps users know what to do next, how to ask an execution agent, and how to inspect the output. It must not replace the user's thinking or produce complete business plans, technical plans, or implementation task lists on the user's behalf.

## Users

The first users are developers, but the skill should work for the whole company: HR, operations, finance, managers, and founders. The first version uses AI-native development as the strongest example while keeping the language broad enough for non-developer work.

## Core Principles

1. Start from the requirement, not from technology.
2. Before adding constraints, remove false constraints.
3. Tell AI the target effect, not the implementation path.
4. Use the SPEC flow for large work: Brainstorm, Grill Me, SPEC, Plan, Tasks, Implementation, Acceptance.
5. Let AI execute, but keep human judgment at business acceptance points.
6. Do not trust AI blindly. Build trust through staged outputs, review checklists, and explicit human confirmation.

## Product Shape

The first version is:

- A reusable skill named `ai-native-methodology-coach`.
- A starter prompt for creating a long-lived methodology coach thread.
- Examples that lower the barrier for teammates who do not know what to ask.
- Checklists that help users judge whether AI outputs can move to the next stage.

No UI, command system, or web app is included in the first version.

## Responsibilities

The skill may:

- Identify the user's current stage.
- Explain the internal methodology basis.
- Ask light clarifying questions.
- Provide prompts for execution threads.
- Provide review checklists.
- Warn when users are steering AI with personal preference, existing implementation bias, or premature technical choices.

The skill must not:

- Write a complete PRD for the user.
- Write a complete technical plan for the user.
- Decompose implementation tasks directly for the user.
- Choose a technology stack unless the methodology source contains a real constraint.
- Give generic AI advice outside the bundled methodology references.

## Knowledge Boundary

The MVP is strict. It answers only from the bundled methodology references derived from the internal notes:

- AI 开发完整流程
- AI 开发核心理念
- AI 测试方法论
- AI 开发工具链与配置
- AI 时代团队转型

If a question is not covered, the skill should say the current methodology does not cover it and suggest adding the question to the methodology backlog.

## Files

```text
skills/ai-native-methodology-coach/
├── SKILL.md
├── REFERENCE.md
├── STARTER_PROMPT.md
├── EXAMPLES.md
└── CHECKLISTS.md
```

## Review

- No unresolved placeholders remain; fill-in fields in prompt templates are intentional.
- Scope is limited to coaching and review.
- The knowledge boundary is explicit.
- The highest-priority principle is requirement-first and subtraction-before-addition.
