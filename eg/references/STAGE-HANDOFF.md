# EG Stage Handoff

## Diagnose -> Precipitate

Optional.

Required when diagnosis ran:

- `/tmp/eg/<run-id>/source-matrix.yml`
- `/tmp/eg/<run-id>/source-gap.yml`
- `/tmp/eg/<run-id>/query-plan.yml` when external queries ran
- `/tmp/eg/<run-id>/diagnosis.yml`
- successful `validate-diagnosis.py`

`eg-diagnose` must not write repo artifacts. `eg-precipitate` consumes only
redacted diagnosis summaries and `handoff_to_precipitate` proposals, then grills
before writing CONTEXT/ADR artifacts.

## Precipitate -> TDD

Required:

- Intent ADR with `status: review` or `approved`.
- `Acceptance Criteria Seed`.
- Related decision/constraint ADRs when they exist.

Missing intent means route to `eg-precipitate` fast-intent. Do not derive BDD from a decision ADR.

## TDD -> Enforce

Required:

- Approved BDD with human approval metadata.
- Frozen `/tmp/eg/<run-id>/enforce-plan.yml` created immediately after BDD approval.
- Planned `/tmp/eg/<run-id>/ci-facts.contract.json` created immediately after BDD approval.
- Verified tests with stable ids in real test names.
- Ready `ci_facts_contract` embedded in `.eg/handoff/<run-id>.yml`.
- Related ADRs and ADR coverage, with every related ADR covered, not-applicable, or deferred.
- `/tmp/eg/<run-id>/ledger.json`.
- Repo `.eg/handoff/<run-id>.yml`.
- Auto commit containing only this EG run's files.

The final handoff must embed the frozen `enforce_plan`. TDD may fill actual
test results and CI-required ids, but must not weaken the frozen baseline after
human BDD approval.

## Enforce Selection

Active handoff:

```text
PR diff touches .eg/handoff/*.yml
AND stage in {tdd-complete, enforce-ready}
AND touched commit is in PR range
AND intent/BDD artifacts exist and are not deprecated
AND related ADR coverage is present
AND enforce_plan is frozen
AND ci_facts_contract is ready
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
If a different fingerprint appears in the same attempted `class_key`, report it as `partial-fix`; the fix agent did not sweep the issue class completely.

The fix-agent must stop if the fix requires changing approved ADR/BDD substance.

Deferred ADR/test coverage goes directly to human decision. It is not a reviewer finding and not agent-fixable without user direction.
