# Checklists

## False Constraint Check

Use this before Plan, refactoring, or SPEC updates.

- Is the constraint required by the business goal?
- Is it required by compliance, data safety, permissions, or security?
- Is it required by team maintenance ability?
- Is it required by migration cost or compatibility?
- Is it required by deployment or runtime limits?
- Is it required by explicit business acceptance?
- Is it only personal preference, dislike, historical habit, current code shape, or a prototype accident?

If it is not a real constraint, remove it before asking AI for a plan or writing it into `comm/`.

## Brainstorm to Grill Me

Ready to move forward when:

- There are multiple possible directions.
- Each direction has a target user or scenario.
- Main risks or unknowns are visible.
- The user has enough context to choose which direction to challenge.

Go back to Brainstorm when:

- There is only one assumed solution.
- The user has locked a technology path without real constraints.
- The problem is still described as a feature instead of a business goal.

## Grill Me to Prototype or Requirement Artifact

Ready to move forward when:

- Important decision points have been challenged.
- Scope and non-scope are clear.
- The user can explain the target outcome in one sentence.
- Known risks have owners or review points.
- Acceptance criteria can be observed.
- Visible flows have enough clarity to prototype, or invisible logic has enough clarity to document.

Go back to Grill Me when:

- The user still says "roughly", "probably", "make it better", or "optimize" without observable meaning.
- There are unresolved trade-offs.
- A hidden technology preference is steering the answer.

## Prototype Review Check

A useful prototype should:

- Validate the core business flow.
- Show the main page or workflow structure.
- Use realistic sample data.
- Include important states such as loading, empty, error, disabled, permission, or approval when relevant.
- Surface open business questions.
- Avoid locking production framework, architecture, analytics, or performance work too early.
- Make it clear what should be removed or delayed.

Go back when:

- It is only a pretty screen.
- It hides unclear decisions.
- It skips key states.
- It is treated as production code.
- It expands scope before validating the core path.

## Prototype to SPEC Impact Check

Do a SPEC impact analysis only when:

- The prototype reveals a reusable rule for many future pages, flows, states, permissions, tests, docs, APIs, or deployments.
- The same pattern already appears in multiple projects.
- The absence of a standard would cause AI drift or team inconsistency.
- A project entrypoint needs to reference an existing `comm/` standard.

Do not update SPEC when:

- The rule is a one-off project choice.
- The flow has not been accepted by humans.
- The rule is only visual polish.
- The rule comes from current implementation habit rather than requirement.

## Requirement Artifact to Plan

Ready to enter Plan when the requirement artifact includes:

- Clear business goal.
- Target users or scenarios.
- Observable acceptance criteria.
- Explicit non-goals.
- Boundaries, risks, permissions, and data concerns.
- Prototype review result when visible flows are involved.
- Applicable `comm/` specs or a clear statement that no shared spec update is needed.
- Enough context for AI to compare approaches.

Do not enter Plan when:

- The requirement is only a solution idea.
- Acceptance is subjective.
- Existing implementation is treated as the only possible design without justification.
- Non-core additions are mixed into the core function too early.
- Applicable shared specs have not been loaded or referenced.

## SPEC System Change Check

A good SPEC change should:

- Serve both humans and AI.
- State what inconsistency, drift, or repeated problem it prevents.
- Apply beyond one request.
- Fit into the `comm/README.md` standard map: group, document, solves, key artifacts.
- Name source artifacts, files, APIs, reports, templates, prompts, or examples.
- Include implementation steps, concrete rules, examples, review checklist, Don't list, and AI upgrade prompt.
- Keep real constraints and remove false constraints.
- Update project entrypoints only when needed.
- Preserve a single source of truth for API fields, error codes, auth rules, and long tables.

Go back when:

- The SPEC is actually a PRD.
- The SPEC is only implementation details.
- It lacks review rules.
- It lacks key artifacts or an AI upgrade prompt.
- It freezes prototype details before business acceptance.
- It would let AI redesign privately without checking shared artifacts.
- It duplicates an existing `comm/` standard.
- It creates duplicated README/API tables or invalid entrypoint references.

## comm Documentation System Check

A healthy `comm/` documentation system should have:

- `comm/README.md` with a standard map: group, document, solves, key artifacts.
- `SYSTEM_DOCUMENTATION_STANDARD.md` as the meta-standard for writing and maintaining project docs.
- Clear responsibility split between root `README.md`, `docs/README.md`, and `AGENTS.md` / `CLAUDE.md`.
- One authoritative API document for fields, error codes, and auth.
- Project entrypoints that reference adopted `comm` specs with valid paths.
- A Don't list that prevents duplicate tables, hidden chat-only constraints, and long-lived temporary notes.

Go back when:

- The standard map cannot tell AI which spec to load.
- Root `README.md` and `docs/README.md` duplicate the same long content.
- API contracts are scattered across multiple docs.
- Key constraints exist only in chat history.
- Project entrypoints reference stale or missing paths.
- The team is adding new standards before extending existing ones.

## Minimum Docs by System Type

External API systems should usually have:

- Root README, `docs/README`, integration guide, API contract, development guide, testing guide.

Master data or multi-consumer systems should add:

- Master-data docs, consumer list, alignment notes.

Compliance or sensitive-data systems should add:

- Security hardening, masking or audit rules, permission matrix.

Internal admin systems can often omit:

- External integration guide, unless internal routes still need an authoritative API contract.

## Plan to Tasks

Ready to move forward when:

- Multiple approaches were compared.
- The chosen approach is tied to the requirement.
- Interfaces and boundaries are clear.
- Risks and rollback or migration concerns are named.
- Applicable specs and project entrypoints are named.
- Multi-agent work has disjoint ownership.

Go back to Plan when:

- The plan is a single unchallenged path.
- It follows the old structure by default.
- It does not explain why the approach satisfies the requirement.
- It ignores shared specs or real constraints.

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
- Whether risk boundaries and shared specs were respected.
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
