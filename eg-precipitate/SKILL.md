---
name: eg-precipitate
description: EG precipitation stage: grill intent, scope, terms, decisions, and constraints into CONTEXT/ADR artifacts.
disable-model-invocation: true
---

# eg-precipitate

Make intent governable. Do not implement, write BDD, run tests, or enforce gates.

Set:

```bash
SKILL_DIR="$(readlink -f .agents/skills/eg-precipitate)"
```

Read shared rules only when the current step needs the contract:

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

Branch completion criterion: a branch is resolved only when it has an explicit term, scope boundary, decision, constraint, non-goal, or defer reason. A plausible answer is not enough.

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

For ADR creation, use deterministic numbering:

```bash
python3 "$SKILL_DIR/scripts/new-adr.py" --repo-root <repo> --title "<title>" --type intent --status approved
python3 "$SKILL_DIR/scripts/new-adr.py" --repo-root <repo> --title "<title>" --type decision --status approved
python3 "$SKILL_DIR/scripts/new-adr.py" --repo-root <repo> --title "<title>" --type constraint --domain security --status approved
```

After writing or editing ADRs, validate them:

```bash
python3 "$SKILL_DIR/scripts/validate-precipitation.py" <repo>/docs/adr/0001-title.md --require-seed
```

Use `--require-seed` for intent ADRs that should hand off to `eg-tdd`.

Write completion criterion: the confirmed artifact exists at the previewed path, validation passed, and any validation failure is reported before asking the next decision question.

## Artifact Rules

- `CONTEXT.md`: durable project language only.
- Intent ADR: business scope and Acceptance Criteria Seed. Only intent ADRs can seed BDD.
- Decision ADR: hard-to-reverse choices with tradeoffs. Never seed BDD.
- Constraint ADR: explicit NFRs with domain.

Before closing an intent ADR, ask the NFR checklist once.

## Intent Approval Gate

Before handing an intent ADR to `eg-tdd`, the write preview must include `status: approved`. After the user confirms, write the ADR and run `validate-precipitation.py --require-seed`.

If the user is not ready to approve, keep `status: review`; `eg-tdd` may only draft/preview BDD and must not approve BDD, freeze plan, write tests, or implement.

## Closing

Summarize only:

- resolved branches and written artifacts
- intent ADRs ready for BDD derivation
- decision ADRs and gates passed
- constraint ADRs and domains
- unresolved branches
- next stage, usually `eg-tdd`
