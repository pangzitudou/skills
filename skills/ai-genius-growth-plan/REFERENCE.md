# AI Genius Growth Plan Reference

This reference is the bundled source of truth for the coach. Do not answer beyond it.

## Core Mindset

AI-native work changes the user's role from controller to goal-setter, reviewer, and acceptor.

- Tell AI the target effect and real constraints, not the implementation path.
- Do not control AI through file paths, frameworks, code shape, or personal technical habits unless the requirement demands it.
- Accept that AI can be imperfect. Use smaller loops, review, QA, and acceptance to reduce risk.
- Focus on business outcome. Users do not need to understand every technical detail when AI can handle execution.
- When stuck, treat the problem itself as something AI can help clarify.

## AI Genius Goal

The goal is not to divide work into frontend, backend, UI, testing, product, or operations roles. The goal is to help every person become an AI-native full-cycle operator.

An AI-native full-cycle operator can:

- Clarify requirements.
- Remove false constraints.
- Use quick prototypes to make abstract ideas visible.
- Ask AI for plans and task breakdowns after requirements are clear.
- Let AI implement, test, tune, and prepare delivery.
- Act as AI's hands, feet, eyes, and business judgment during QA and acceptance.
- Maintain shared constraints through `comm/` SPEC documents when a reusable standard is needed.

## Maximum Value

The largest value is not faster coding. It is reducing communication loss across requirement, design, development, testing, and acceptance; finding better solutions than the user has personally seen; and lowering the threshold for creating useful outcomes.

## Requirement-First Rule

Start with the requirement, target effect, boundaries, and acceptance criteria.

Do not start with:

- A favorite technology stack.
- A disliked technology stack.
- The current code structure.
- Existing team habit.
- A premature implementation path.
- Nice-to-have additions such as analytics, performance tuning, or polish before the core function is clear.
- A desire to write or update SPEC before knowing whether a reusable constraint is needed.

Before adding anything, remove false constraints. A constraint is real only when it affects the business goal, risk boundary, compliance, data safety, permissions, security, maintenance ability, migration cost, deployment, compatibility, or explicit acceptance.

## Main Flow

For new or complex work, use this flow:

1. Brainstorm: diverge from a raw idea into possible directions.
2. Grill Me: converge by questioning important decision points.
3. Prototype when useful: use quick HTML to validate visible flow, information architecture, interaction, and state.
4. Requirement artifact: record the agreed target, users, flow, constraints, non-goals, and acceptance criteria in the project's normal artifact format.
5. Plan: ask AI for multiple technical approaches after the requirement is clear and applicable shared specs are loaded.
6. Tasks: split the chosen plan into executable tasks.
7. Implementation: let AI develop, test, tune, and prepare delivery.
8. Human QA and Acceptance: AI drafts QA; humans verify real behavior and business outcome.

Brainstorm answers "what should we do and where could this go?" Grill Me answers "are decisions clear enough to avoid rework?" Prototype answers "can stakeholders see and judge the flow?" Requirement artifact answers "what exactly are we asking execution threads to satisfy?"

## SPEC / comm System

SPEC is the team's shared Specification Documents System, not a one-off requirement document and not an AI tool feature.

Typical structure:

```text
comm/
  README.md
  SYSTEM_DOCUMENTATION_STANDARD.md
  INTERNAL_UI_DESIGN_SPEC.md
  EXTERNAL_OPEN_API_PLATFORM_STANDARD.md
  WEB_SERVICE_TECH_STACK_STANDARD.md
  ...

project/
  AGENTS.md / CLAUDE.md / README.md
  docs/
  ...
```

`comm/` stores reusable standards. Project entrypoints reference those standards and add project-specific conventions. This lets humans copy proven rules and lets AI load the right context without private redesign.

SPEC is a cross-cutting constraint layer:

- Before Plan: load applicable specs and distinguish real constraints from false constraints.
- During prototype review: decide whether a repeated or reusable rule should be proposed for `comm/`.
- Before Implementation: check that execution threads know which specs apply.
- After Acceptance: update specs only if the team learned a reusable rule.

Do not put one-off decisions, unvalidated prototype ideas, or personal technology preferences into `comm/`.

For detailed guidance, use [SPEC_GUIDE.md](SPEC_GUIDE.md).

## Prompting Principles

- Do not start with role-play such as "you are an excellent engineer".
- Say what you want to achieve.
- Give enough context.
- Describe the desired effect.
- Avoid prescribing the implementation path unless it is a real constraint.
- When shared specs apply, point AI to the relevant `comm/` documents through the project entrypoint instead of pasting everything manually.

## HTML Prototyping

When work involves user flow, screens, operations, state changes, or information architecture, use a quick HTML prototype before Plan or implementation. The prototype is not production code. It is a fast requirement validation artifact for everyone.

After prototype, review:

- What the prototype validated.
- What is still uncertain.
- What should be removed or delayed.
- What is ready for the requirement artifact.
- Whether any reusable rule should trigger a SPEC impact analysis.

Use [PROTOTYPING_GUIDE.md](PROTOTYPING_GUIDE.md) for details.

## Multi-Agent Collaboration

Use multiple agents when work has separate modules or responsibilities.

Recommended pattern:

1. Ask an architect thread to create separate prompts for separate agents.
2. Ensure interfaces and boundaries match.
3. Ask AI to review the prompts for risk before execution.
4. Give each agent disjoint files or modules to reduce conflict.
5. Ensure each agent loads the applicable project entrypoint and shared specs.

The growth coach should help prepare and review prompts, not execute module work itself.

## Testing Methodology

Testing is layered:

1. Unit tests: AI can write these and cover basic logic, but passing unit tests does not prove the real product works.
2. E2E tests: AI plus tools such as Playwright can cover smoke-level behavior, but reliability is still limited.
3. Human QA: humans act as AI's hands, feet, and eyes in real or staging environments.
4. Product acceptance: humans verify the business outcome.

Improve testing by asking AI to propose QA plans, asking AI to self-review, and using another AI to find missing cases.

Add analytics, performance tuning, and similar non-core work late. Early extra requirements can distract AI from the core function.

Use [HUMAN_QA_GUIDE.md](HUMAN_QA_GUIDE.md) when the user needs manual validation steps, bug feedback templates, or acceptance guidance.

## Team Adoption

The tool should help the whole company experience AI-native work. The target is not role specialization; the target is raising everyone toward AI-native full-cycle ability.

For non-development work, translate the same flow:

- Clarify the target outcome.
- Remove false constraints.
- Use prototypes or examples when the flow is hard to judge in text.
- Let AI propose a process or artifact in an execution thread.
- Review using a checklist.
- Keep human approval for high-risk or business-critical decisions.

Use [FIRST_USE.md](FIRST_USE.md) when the user needs a starting point.

## Project Usage

A long-lived growth coach thread can be shared across projects because the methodology is common. Specific execution work should happen in separate project threads. Bring outputs back to the coach thread for review.

When work touches a real codebase, the project entrypoint should reference applicable `comm/` specs. The coach may ask the user to bring back the entrypoint or spec impact analysis.

## Methodology Evolution

When a question is not covered, treat it as a methodology gap, not as an invitation to improvise. Use [METHODOLOGY_GAPS.md](METHODOLOGY_GAPS.md) to record what is missing and where it should be added.
