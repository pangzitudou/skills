---
name: eg-precipitate
description: "Strict Executable Governance precipitation: grill intent, scope, terms, decisions, and constraints until stable, then write CONTEXT/ADR artifacts after one preview confirmation. Use for EG fast-intent, governance precipitation, unclear feature intent, scope boundaries, decision tradeoffs, NFR constraints, or when eg-router routes to precipitate."
---

# eg-precipitate

Make intent governable. Do not implement, write BDD, run tests, or enforce gates.

Read shared rules when needed:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Load local references only for the current branch:

- Interaction and decision tree pressure: `references/interaction-protocol.md`
- Artifact eligibility: `references/precipitation-triggers.md`
- CONTEXT/ADR formats: `references/artifact-formats.md`
- NFR checkpoint: `references/nfr-checklist.md`
- Failure modes: `references/failure-modes.md`

## Loop

Walk the decision tree one branch at a time until shared understanding is stable enough for the next stage.

Per turn:

```md
Current decision: ...
Decision tree state:
- Resolved: ...
- Active branch: ...
- Unresolved: ...
- Blocked: ...

Recommended answer: ...
Hard question: ...
Potential write: ...
```

Ask one hard question. If code or existing artifacts can answer it, inspect them instead of asking.

## Write Policy

Default: do not write.

Write only when a term, scope boundary, decision, or constraint is stable enough to govern future work.

Use one confirmation:

```md
Write preview:
- Artifact: CONTEXT.md | ADR
- Content: ...
- Reason: ...

Confirm write?
```

After confirmation, write immediately. Do not ask again unless the preview is no longer accurate, the path conflicts, multiple artifacts were not all confirmed, or approved artifact substance would change.

## Artifact Rules

- `CONTEXT.md`: durable project language only.
- Intent ADR: business scope and Acceptance Criteria Seed. Only intent ADRs can seed BDD.
- Decision ADR: hard-to-reverse choices with tradeoffs. Never seed BDD.
- Constraint ADR: explicit NFRs with domain.

Before closing an intent ADR, ask the NFR checklist once.

## Closing

Summarize only:

- resolved branches and written artifacts
- intent ADRs ready for BDD derivation
- decision ADRs and gates passed
- constraint ADRs and domains
- unresolved branches
- next stage, usually `eg-tdd`
