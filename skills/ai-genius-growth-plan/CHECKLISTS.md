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

If it is not a real constraint, remove it before asking AI for a plan or writing it into SPEC.

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

## Grill Me to Prototype or SPEC

Ready to move forward when:

- Important decision points have been challenged.
- Scope and non-scope are clear.
- The user can explain the target outcome in one sentence.
- Known risks have owners or review points.
- Acceptance criteria can be observed.
- Visible flows have enough clarity to prototype, or invisible logic has enough clarity to write SPEC.

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

## Prototype to SPEC Check

Ready to draft or update a project/feature SPEC when:

- The core user path has been reviewed by a human.
- The accepted states and unresolved states are separated.
- The goal, users, scope, non-goals, business rules, and acceptance can be written as a contract.
- UI decisions are tied to business flow or acceptance, not personal visual taste.
- Non-core additions have been removed or deferred.

Do not draft SPEC from prototype when:

- Stakeholders have not reviewed the prototype.
- The prototype is mostly visual polish.
- The flow is still ambiguous.
- The user is trying to avoid clarifying rules by writing a document.

Run a common SPEC impact check only when the prototype reveals a reusable rule across projects.

## SPEC Contract Check

A good project or feature SPEC should include:

- Business goal.
- User roles and core scenarios.
- Functional scope.
- Explicit non-goals.
- Business flow.
- Business rules.
- Permission, security, and data boundaries.
- API capability summary when APIs matter.
- Data object summary when data matters.
- Non-functional requirements at requirement level.
- Acceptance criteria.
- Don't list.
- References to detailed documents for API, data model, testing, deployment, architecture, or README details.

Go back when:

- The SPEC starts with implementation or technology choices.
- It contains startup commands.
- It contains full API request and response field tables.
- It contains database table DDL or full schema details.
- It contains controller/service/repository implementation paths.
- It contains test command or detailed test-case procedures.
- It contains deployment commands.
- It stores temporary discussion notes or discarded ideas.
- It lacks acceptance criteria.
- It does not say what is out of scope.

## SPEC to Plan

Ready to enter Plan when the SPEC includes:

- Clear business goal.
- Target users or scenarios.
- Observable acceptance criteria.
- Explicit non-goals.
- Boundaries, risks, permissions, and data concerns.
- Prototype review result when visible flows are involved.
- Applicable common specs or a clear statement that none apply.
- References to the right detailed docs instead of duplicating them.
- Enough context for AI to compare approaches.

Do not enter Plan when:

- The requirement is only a solution idea.
- Acceptance is subjective.
- Existing implementation is treated as the only possible design without justification.
- Non-core additions are mixed into the core function too early.
- Applicable common specs have not been loaded or referenced.
- API, data, test, or deployment details are pretending to be SPEC.

## Common SPEC Impact Check

Use this only for company-level or shared standards.

A common SPEC change should:

- Apply beyond one request.
- Prevent repeated drift, inconsistency, risk, or review failure.
- Preserve a clear boundary with project SPEC, README, API, data model, testing, and deployment docs.
- Fit into the shared standard map if one exists.
- Keep real constraints and remove false constraints.
- Update project entrypoints only when needed.
- Preserve a single source of truth for API fields, error codes, auth rules, and long tables.

Go back when:

- The proposed common SPEC is actually one project's feature SPEC.
- It freezes unaccepted prototype details.
- It standardizes personal preference or current implementation shape.
- It duplicates another shared standard.
- It creates duplicated README/API/TESTING content.
- It adds new standards before extending an existing one.

## Documentation Boundary Check

Use this when SPEC starts absorbing other docs.

- SPEC: goal, roles, scope, flow, rules, boundaries, acceptance.
- README: project identity, brief setup, brief test command, docs entry.
- ARCHITECTURE: modules, dependencies, technical choices, implementation rationale.
- API: paths, fields, auth headers, error codes, examples.
- DATA_MODEL or DATABASE: entities, fields, relationships, SQL, migrations.
- TESTING: strategy, commands, cases, fixtures, regression.
- DEPLOYMENT: env vars, deployment, rollback, operations.
- CHANGELOG: change history.
- DECISIONS: key decisions and rationale.

Go back when:

- A table is maintained in two places.
- API fields appear in SPEC and API docs at the same level of detail.
- Test cases are mixed into acceptance criteria.
- Commands or implementation paths appear in SPEC.

## Plan to Tasks

Ready to move forward when:

- Multiple approaches were compared.
- The chosen approach is tied to the SPEC.
- Interfaces and boundaries are clear.
- Risks and rollback or migration concerns are named.
- Applicable specs and project entrypoints are named.
- Multi-agent work has disjoint ownership.

Go back to Plan when:

- The plan is a single unchallenged path.
- It follows the old structure by default.
- It does not explain why the approach satisfies the SPEC.
- It ignores common specs or real constraints.

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
- Whether risk boundaries and applicable specs were respected.
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
