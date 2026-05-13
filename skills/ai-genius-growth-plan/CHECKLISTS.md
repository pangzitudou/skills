# Checklists

## False Constraint Check

Use this before Plan or refactoring.

- Is the constraint required by the business goal?
- Is it required by compliance, data safety, permissions, or security?
- Is it required by team maintenance ability?
- Is it required by migration cost or compatibility?
- Is it required by deployment or runtime limits?
- Is it only personal preference, dislike, historical habit, or current code shape?

If it is not a real constraint, remove it before asking AI for a plan.

## Brainstorm to Grill Me

Ready to move forward when:

- There are multiple possible directions.
- Each direction has a target user or scenario.
- Main risks or unknowns are visible.
- The user has enough context to choose which direction to challenge.

Go back to Brainstorm when:

- There is only one assumed solution.
- The user has already locked a technology path without real constraints.
- The problem is still described as a feature instead of a business goal.

## Grill Me to SPEC

Ready to move forward when:

- Important decision points have been challenged.
- Scope and non-scope are clear.
- The user can explain the target outcome in one sentence.
- Known risks have owners or review points.
- Acceptance criteria can be observed.

Go back to Grill Me when:

- The user still says "roughly", "probably", "make it better", or "optimize" without observable meaning.
- There are unresolved trade-offs.
- A hidden technology preference is steering the answer.

## SPEC to Plan

Ready to move forward when the PRD or SPEC includes:

- Clear business goal.
- Target users or scenarios.
- Observable acceptance criteria.
- Explicit non-goals.
- Boundaries, risks, permissions, and data concerns.
- Enough context for AI to compare approaches.
- Relevant standards, files, modules, APIs, docs, or artifacts that AI must load.
- Review checklist and Don't list.
- HTML prototype for visible flows when the requirement involves screens, workflows, or user operations.

Do not enter Plan when:

- The requirement is only a solution idea.
- Acceptance is subjective.
- Existing implementation is treated as the only possible design without justification.
- Non-core additions are mixed into the core function too early.

## HTML Prototype Check

A useful prototype should:

- Validate the core business flow.
- Show the main page or workflow structure.
- Use realistic sample data.
- Include important states such as loading, empty, error, disabled, permission, or approval when relevant.
- Surface open business questions.
- Avoid locking production framework, architecture, analytics, or performance work too early.

Go back when:

- It is only a pretty screen.
- It hides unclear decisions.
- It skips key states.
- It is treated as production code.
- It expands scope before validating the core path.

## SPEC Quality Check

A good SPEC should:

- Serve both humans and AI.
- State the purpose, audience, scope, and source of truth.
- Explain the update rule.
- Provide execution steps.
- Include a quick index or standard map when the domain is broad.
- Name key artifacts, files, APIs, reports, templates, or prompts.
- Include principles, concrete rules, review checklist, Don't list, and AI upgrade prompt.
- Keep real constraints and remove false constraints.

Go back to Grill Me when:

- The SPEC cannot explain what problem it standardizes.
- The SPEC is only a list of implementation details.
- The SPEC lacks acceptance or review rules.
- The SPEC would let AI redesign privately without checking shared artifacts.

## Plan to Tasks

Ready to move forward when:

- Multiple approaches were compared.
- The chosen approach is tied to the requirement.
- Interfaces and boundaries are clear.
- Risks and rollback or migration concerns are named.
- Multi-agent work has disjoint ownership.

Go back to Plan when:

- The plan is a single unchallenged path.
- It follows the old structure by default.
- It does not explain why the approach satisfies the requirement.

## Implementation Acceptance

AI should cover:

- Unit tests for core logic.
- Smoke-level E2E where possible.
- Self-review of changes.
- QA checklist generation.
- Fixes after test or browser feedback.

Humans should cover:

- Real or staging environment operation.
- Evidence capture: screenshots, logs, URLs, timestamps, and exact data.
- Whether the output achieves the business goal.
- Whether the user experience or operational process is acceptable.
- Whether risk boundaries were respected.
- Whether the result should be shipped, revised, or rejected.

Remember: unit tests passing does not prove the product works. Product acceptance is the human role.

## Human QA Check

Ready for business acceptance when:

- AI generated a step-by-step QA plan.
- Human ran the happy path in a real or staging environment.
- Human checked key states: loading, empty, error, disabled, permission, approval, pagination, or data edge cases when relevant.
- Failures were reported with steps, actual result, expected result, evidence, and business impact.
- AI fixed or explained failures.
- The human can state whether the business goal is achieved.

Go back when:

- The user only clicked around without a QA plan.
- AI only says "tests passed".
- Failures are described vaguely.
- Human begins manual code debugging instead of feeding evidence back to AI.
- The final decision is based on technical confidence rather than business acceptance.

## Methodology Gap Check

Use this when a question is not covered.

- What exactly did the user ask?
- Which current reference failed to cover it?
- Is the missing piece a stage rule, checklist, role example, risk boundary, standard pattern, or anti-pattern?
- Which file should be updated?
- What is the smallest useful addition?

Do not answer with generic advice before the methodology is updated.
