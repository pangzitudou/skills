---
name: eg-tdd
description: EG TDD stage: approved intent -> approved BDD -> tests -> implementation -> handoff -> scoped commit.
disable-model-invocation: true
---

# eg-tdd

Turn approved intent into approved BDD, verified tests, minimal implementation, repo handoff, and commit.

Set:

```bash
SKILL_DIR="$(readlink -f .agents/skills/eg-tdd)"
```

Shared rules:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Local references:

- BDD format and preview: `BDD-FORMAT.md`
- Handoff format: `HANDOFF-FORMAT.md`
- Ledger schema reference: `governance.schema.json`
- CI facts shape: `../eg-enforce/CI-FACTS-FORMAT.md`

## Required Start

Input must include exactly one active intent ADR in `docs/adr/` with:

- `type: intent`
- `status: review` or `approved`
- `Acceptance Criteria Seed`

If missing, draft, or only a decision ADR exists, stop and return to `eg-precipitate` fast-intent. If multiple intent ADRs could apply, ask which one governs this run. BDD must derive from intent ADR. `review` intent may only produce BDD draft/preview; intent must be `approved` before freezing the enforce plan or writing tests.

Create run state before any test:

```bash
python3 "$SKILL_DIR/scripts/new-governance.py" \
  --repo <repo-name> --task <task-slug> --mode lite --intent-adr ADR-NNNN
```

Use `--mode full` for bug fixes, permissions, idempotency/retry, concurrency, transactions, database changes, external contracts, webhooks, async work, or cross-module orchestration.

Start completion criterion: the run has a `/tmp/eg/<run-id>/ledger.json` tied to one intent ADR, or the agent has stopped with the exact missing intent decision.

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
- freeze enforce-plan and CI facts contract
- continue to acceptance tests and TDD
```

5. Before approving BDD, ensure the intent ADR is `status: approved`. If it is still `review`, keep BDD as draft and route back to `eg-precipitate` for intent approval.
6. If user approves, set `status: approved`, add `approved_by`, `approved_at`, and `approval_source`, then continue to freeze baseline. Do not stop before freezing, even if the user asks to stop after approval.
7. If the user requests changes, keep draft, revise, and preview again.
8. Fill `/tmp/eg/<run-id>/ledger.json` with frozen-baseline inputs:
   - `bdd`
   - `related_adrs`
   - `enforce_plan.required_acceptance_tests`
   - `enforce_plan.expected_adversarial_domains`
   - `enforce_plan.manual_qa_expected`
   - `enforce_plan.out_of_scope`
   - `enforce_plan.nfr_checkpoints`
   - `ci_facts_contract.path`
   - `ci_facts_contract.producer`
9. Freeze enforce handoff baseline:

```bash
python3 "$SKILL_DIR/scripts/freeze-enforce-plan.py" /tmp/eg/<run-id>/ledger.json
```

This writes `/tmp/eg/<run-id>/enforce-plan.yml` and `/tmp/eg/<run-id>/ci-facts.contract.json`.
The script also writes `frozen_enforce_plan_hash` into the ledger. Later validation must match the ledger plan, hash, and frozen file.

Never write tests before explicit BDD approval.
If the user asked to stop after BDD approval, stop only after approval metadata is written and `freeze-enforce-plan.py` succeeds.

Gate 1 completion criterion: either BDD remains draft with a concrete human question, or approved BDD metadata exists and `freeze-enforce-plan.py` has written both `enforce-plan.yml` and `ci-facts.contract.json`.

## Gate 2: Tests, Implementation, Handoff

1. Complete `/tmp/eg/<run-id>/ledger.json`.
   - `related_adrs` must still match the frozen `enforce_plan.related_adrs`.
   - `adr_coverage` must classify every related ADR as `covered`, `not-applicable`, or `deferred`.
   - `ci_facts_contract.expected_acceptance_test_ids` must match frozen planned AT ids.
2. Run planning validation:

```bash
python3 "$SKILL_DIR/scripts/validate-governance.py" /tmp/eg/<run-id>/ledger.json --phase planning --repo-root <repo>
```

3. Write acceptance tests first. Each test id must be in the real test name and derive from a BDD scenario.
4. Confirm RED fails for the intended behavior.
5. Generate adversarial hypotheses before non-AT tests. Expected outcomes must cite BDD, spec, ADR, requirement, or contract; implementation-only oracle is invalid.
6. For accepted hypotheses, drive RED -> GREEN -> sensitivity review.
7. Before final validation, set:
   - `ci_facts_contract.status: ready`
   - `ci_facts_contract.required_result_ids`: exactly every `AT-*` or `H*` with `status: green` or `merged`
8. Validate final and emit handoff:

```bash
python3 "$SKILL_DIR/scripts/validate-governance.py" \
  /tmp/eg/<run-id>/ledger.json \
  --repo-root <repo> \
  --emit-handoff <repo>/.eg/handoff/<run-id>.yml
```

The handoff command refuses to overwrite an existing `.eg/handoff/<run-id>.yml` unless `--force-handoff` is explicitly passed.

9. Print a commit plan, then auto-commit only touched EG-run files. Do not ask again.

Gate 2 completion criterion: final validation emitted `.eg/handoff/<run-id>.yml`, every green or merged test has a required CI fact id, and a scoped commit exists unless unrelated dirty overlap blocked it.

Coverage and CI facts rules live in `../eg/references/ARTIFACT-MODEL.md` and `HANDOFF-FORMAT.md`. Gate 2 must satisfy final validation: no related ADR may be absent, the frozen `enforce_plan` may not be weakened, and no green or merged test may lack a required CI fact id.

## Auto Commit

Commit only after final validation passes and required tests run green.

Do:

- `git status --short`
- add only code, tests, BDD/ADR status changes, and `.eg/handoff/<run-id>.yml`
- run `python3 "$SKILL_DIR/scripts/validate-commit-scope.py" --repo-root <repo> --ledger /tmp/eg/<run-id>/ledger.json --handoff <repo>/.eg/handoff/<run-id>.yml`
- commit with `Intent`, `BDD`, and `Run` in the message

Stop if related files overlap unrelated dirty changes. Never commit `/tmp/eg`.

## Never

- Invent business intent.
- Derive BDD from a decision ADR.
- Write tests against draft/review BDD.
- Edit approved ADR/BDD substance to make code pass.
- Let implementation define the assertion oracle.
- Emit enforcement level or gate judgment.
