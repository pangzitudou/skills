---
name: eg-tdd
description: "Executable Governance dev loop after intent exists: derive draft BDD from intent, show human preview, approve BDD with metadata, write acceptance tests and adversarial TDD tests, emit /tmp/eg ledger plus .eg/handoff manifest, and auto-commit verified scoped changes. Use when implementing under EG, deriving BDD/tests, or when eg-router routes to TDD."
---

# eg-tdd

Turn approved intent into approved BDD, verified tests, minimal implementation, repo handoff, and commit.

Shared rules:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Local references:

- BDD format and preview: `BDD-FORMAT.md`
- Handoff format: `HANDOFF-FORMAT.md`
- Ledger schema reference: `governance.schema.json`

## Required Start

Input must include an intent ADR in `docs/adr/` with:

- `type: intent`
- `status: review` or `approved`
- `Acceptance Criteria Seed`

If missing, draft, or only a decision ADR exists, stop and return to `eg-precipitate` fast-intent. BDD must derive from intent ADR.

Create run state before any test:

```bash
python3 ../eg-tdd/scripts/new-governance.py \
  --repo <repo-name> --task <task-slug> --mode lite --intent-adr ADR-NNNN
```

Use `--mode full` for bug fixes, permissions, idempotency/retry, concurrency, transactions, database changes, external contracts, webhooks, async work, or cross-module orchestration.

## Gate 1: BDD Approval

1. Read intent, related decision/constraint ADRs, and local `CONTEXT.md`.
2. Write draft BDD directly in `docs/bdd/` with `status: draft`.
3. For every Acceptance Criteria Seed item, derive at least one happy scenario and one edge/negative scenario.
4. Show a human-readable preview:

```md
BDD preview:
...

Approve?
If approved, I will:
- set this BDD to approved with approval metadata
- continue to acceptance tests and TDD
```

5. If user approves, set `status: approved`, add `approved_by`, `approved_at`, and `approval_source`, then continue. If the user asks to stop, stop after approval.
6. If the user requests changes, keep draft, revise, and preview again.

Never write tests before explicit BDD approval.

## Gate 2: Tests, Implementation, Handoff

1. Fill `/tmp/eg/<run-id>/ledger.json`.
   - `related_adrs` must include the intent ADR and every related decision/constraint ADR read or referenced.
   - `adr_coverage` must classify every related ADR as `covered`, `not-applicable`, or `deferred`.
2. Run planning validation:

```bash
python3 ../eg-tdd/scripts/validate-governance.py /tmp/eg/<run-id>/ledger.json --phase planning --repo-root <repo>
```

3. Write acceptance tests first. Each test id must be in the real test name and derive from a BDD scenario.
4. Confirm RED fails for the intended behavior.
5. Generate adversarial hypotheses before non-AT tests. Expected outcomes must cite BDD, spec, ADR, requirement, or contract; implementation-only oracle is invalid.
6. For accepted hypotheses, drive RED -> GREEN -> sensitivity review.
7. Validate final and emit handoff:

```bash
python3 ../eg-tdd/scripts/validate-governance.py \
  /tmp/eg/<run-id>/ledger.json \
  --repo-root <repo> \
  --emit-handoff <repo>/.eg/handoff/<run-id>.yml
```

8. Print a commit plan, then auto-commit only touched EG-run files. Do not ask again.

ADR coverage rules:

- Intent ADR must be `covered` by a BDD scenario and an AT.
- Constraint ADR must be covered by `H*` or `manual_qa:*`, unless explicitly `not-applicable` or `deferred`.
- Decision ADR may be `not-applicable`, but must not be absent.

## Auto Commit

Commit only after final validation passes and required tests run green.

Do:

- `git status --short`
- add only code, tests, BDD/ADR status changes, and `.eg/handoff/<run-id>.yml`
- commit with `Intent`, `BDD`, and `Run` in the message

Stop if related files overlap unrelated dirty changes. Never commit `/tmp/eg`.

## Never

- Invent business intent.
- Derive BDD from a decision ADR.
- Write tests against draft/review BDD.
- Edit approved ADR/BDD substance to make code pass.
- Let implementation define the assertion oracle.
- Emit enforcement level or gate judgment.
