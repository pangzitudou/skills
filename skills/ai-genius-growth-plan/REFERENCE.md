# AI Genius Growth Plan Reference

This reference is the bundled source of truth for the first version of the coach. Do not answer beyond it.

## Core Mindset

AI-native work changes the user's role from controller to goal-setter and acceptor.

- Do not control AI through file paths, implementation steps, or personal technical habits when the requirement does not demand them.
- Tell AI the target effect and constraints, not the path.
- Accept that AI can be imperfect. Use iteration, review, and acceptance to reduce risk.
- Focus on business outcome. Users do not need to understand every technical detail when AI can handle execution.
- When stuck, treat the problem itself as something AI can help solve.

## AI Genius Goal

The goal is not to divide work into frontend, backend, UI, testing, product, or operations roles. The goal is to help every person become an AI-native full-cycle operator.

An AI-native full-cycle operator can:

- Clarify requirements.
- Remove false constraints.
- Use quick prototypes to make abstract ideas visible.
- Ask AI for plans and task breakdowns.
- Let AI implement, test, and tune.
- Use checklists and human judgment to accept business outcomes.

## Maximum Value

The largest value is not faster coding. It is reducing communication loss across requirement, design, development, and testing; finding better solutions than the user has personally seen; and lowering the professional threshold for creating useful outcomes.

## Requirement-First Rule

Start with the requirement, target effect, boundaries, and acceptance criteria.

Do not start with:

- A favorite technology stack.
- A disliked technology stack.
- The current code structure.
- Existing team habit.
- A premature implementation path.
- Nice-to-have additions such as analytics, performance tuning, or polish before the core function is clear.

Before adding anything, remove false constraints. A constraint is real only when it affects the business goal, risk boundary, compliance, data safety, maintenance ability, migration cost, deployment, compatibility, or explicit acceptance.

## SPEC Flow

For new or complex work, use this flow:

1. Brainstorm: diverge from a raw idea into possible directions.
2. Grill Me: converge by questioning every important decision point.
3. Prototype when useful: use quick HTML to validate visible flow, information architecture, interaction, and state.
4. SPEC: structure the requirement into a clear document.
5. Plan: ask AI for multiple technical approaches after the requirement is clear.
6. Tasks: split the chosen plan into executable tasks.
7. Implementation: let AI develop, test, tune, commit, and deploy.
8. Acceptance: human checks whether the result achieves the business goal.

Brainstorm answers "what should we do and where could this go?" Grill Me answers "are all decisions clear enough to avoid rework?"

## SPEC as Shared Context

A SPEC is not only a requirement document. It is a shared context interface for humans and AI.

It should tell humans:

- What standard to follow.
- What order to execute.
- What artifacts are expected.
- What is forbidden.
- How to check whether the output is acceptable.

It should tell AI:

- What context to load.
- What constraints must not be violated.
- What files, modules, APIs, documents, or artifacts are involved.
- What prompt or review pattern to use when upgrading or generating work.
- How to avoid private redesign, drift, and local inconsistency.

For detailed structure, use [SPEC_GUIDE.md](SPEC_GUIDE.md).

## Prompting Principles

- Do not start with role-play such as "you are an excellent engineer".
- Say what you want to achieve.
- Give enough context.
- Describe the desired effect.
- Avoid prescribing the implementation path unless it is a real constraint.

## HTML Prototyping

When work involves user flow, screens, operations, state changes, or information architecture, use a quick HTML prototype before Plan or implementation. The prototype is not a frontend task and not production code. It is a fast requirement validation artifact for everyone.

Use [PROTOTYPING_GUIDE.md](PROTOTYPING_GUIDE.md) for details.

## Multi-Agent Collaboration

Use multiple agents when work has separate modules or responsibilities.

Recommended pattern:

1. Ask an architect thread to create separate prompts for separate agents.
2. Ensure interfaces and boundaries match.
3. Ask AI to review the prompts for risk before execution.
4. Give each agent disjoint files or modules to reduce conflict.

The growth coach should help prepare and review these prompts, not execute the module work itself.

## Testing Methodology

Testing is layered:

1. Unit tests: AI can write these and cover basic logic, but passing unit tests does not prove the real product works.
2. E2E tests: AI plus tools such as Playwright can cover smoke-level behavior, but reliability is still limited.
3. Product acceptance: humans verify the business outcome.

Improve testing by asking AI to propose QA plans, asking AI to self-review, and using another AI to find missing cases.

Add analytics, performance tuning, and similar non-core work late. Early extra requirements can distract AI from the core function.

## Team Adoption

The tool should help the whole company experience AI-native work. The target is not role specialization; the target is raising everyone toward AI-native full-cycle ability.

For non-development work, translate the same flow:

- Clarify the target outcome.
- Remove false constraints.
- Let AI propose the process or artifact in an execution thread.
- Review using a checklist.
- Keep human approval for high-risk or business-critical decisions.

Use [FIRST_USE.md](FIRST_USE.md) when the user needs a role-specific starting point.

## Project Usage

A long-lived growth coach thread can be shared across projects because the methodology is common. Specific execution work should happen in separate project threads. Bring outputs back to the coach thread for review.

## Methodology Evolution

When a question is not covered, treat it as a methodology gap, not as an invitation to improvise. Use [METHODOLOGY_GAPS.md](METHODOLOGY_GAPS.md) to record what is missing and where it should be added.
