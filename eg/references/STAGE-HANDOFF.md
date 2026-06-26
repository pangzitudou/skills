# EG Stage Handoff

## Precipitate -> TDD

Required:

- Intent ADR with `status: review` or `approved`.
- `Acceptance Criteria Seed`.
- Related decision/constraint ADRs when they exist.

Missing intent means route to `eg-precipitate` fast-intent. Do not derive BDD from a decision ADR.

## TDD -> Enforce

Required:

- Approved BDD with human approval metadata.
- Verified tests with stable ids in real test names.
- Related ADRs and ADR coverage, with every related ADR covered, not-applicable, or deferred.
- `/tmp/eg/<run-id>/ledger.json`.
- Repo `.eg/handoff/<run-id>.yml`.
- Auto commit containing only this EG run's files.

## Enforce Selection

Active handoff:

```text
PR diff touches .eg/handoff/*.yml
AND stage in {tdd-complete, enforce-ready}
AND touched commit is in PR range
AND intent/BDD artifacts exist and are not deprecated
AND related ADR coverage is present
```

First version uses `tdd-complete` only.

`eg-enforce` does not write back `stage: enforced`; it reports to `/tmp/eg/<run-id>/feedback.json`, CI, and human-facing comments/messages.

Each enforce round also updates:

```text
/tmp/eg/<run-id>/finding-ledger.json
```

The ledger is the source of truth for finding lifecycle: `new`, `persisted`, `partial-fix`, `regression`, `closed`, `superseded`.

## Enforce Next Question

Ask exactly one next question using this priority:

1. Human decision.
2. Generate fix-agent handoff.
3. Prepare manual QA checklist.
4. Pass/no action.

If agent-fixable findings exist, ask whether to generate:

```text
/tmp/eg/<run-id>/fix-handoff.md
```

Generate it from `/tmp/eg/<run-id>/finding-ledger.json`, not directly from raw findings. It must include fingerprints and closure requirements.

The fix-agent must verify, auto-commit only fix-scope files, and write:

```text
/tmp/eg/<run-id>/closure-evidence.json
```

The next enforce round consumes closure evidence. If a fingerprint remains present after closure evidence, report it as `partial-fix`. If a closed fingerprint reappears, report it as `regression`.

The fix-agent must stop if the fix requires changing approved ADR/BDD substance.

Deferred ADR/test coverage goes directly to human decision. It is not a reviewer finding and not agent-fixable without user direction.
