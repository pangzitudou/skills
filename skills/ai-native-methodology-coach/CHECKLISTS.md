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

Do not enter Plan when:

- The requirement is only a solution idea.
- Acceptance is subjective.
- Existing implementation is treated as the only possible design without justification.
- Non-core additions are mixed into the core function too early.

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
- Fixes after test or browser feedback.

Humans should cover:

- Whether the output achieves the business goal.
- Whether the user experience or operational process is acceptable.
- Whether risk boundaries were respected.
- Whether the result should be shipped, revised, or rejected.

Remember: unit tests passing does not prove the product works. Product acceptance is the human role.

