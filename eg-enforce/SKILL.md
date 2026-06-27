---
name: eg-enforce
description: EG enforce stage: PR gate from handoffs, CI facts, isolated reviews, lifecycle ledger, and one next question.
disable-model-invocation: true
---

# eg-enforce

Run the PR-time EG outer loop. Report gate and ask one next question. Do not fix code.

Set:

```bash
SKILL_DIR="$(readlink -f .agents/skills/eg-enforce)"
```

Shared references:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Local references:

- `QUALITY-REVIEW.md`
- `QUALITY-RULES.md`
- `ARTIFACT-REVIEW.md`
- `FINDING-LIFECYCLE.md`
- `CI-FACTS-FORMAT.md`
- `enforcement.default.yml`
- `findings.schema.json`

## Invariants

- Reviewers identify findings only.
- `scripts/enforce.py` alone assigns enforcement level, next step, waiver consumption, and gate.
- Artifact status may enter enforcement. Enforcement level never comes from upstream artifacts, CI, handoff, or reviewers.
- Reviewers are isolated. Do not pass conversation history, implementer rationale, or `/tmp/eg` ledger into reviewer subagents.
- CI owns test execution. This skill reads CI facts; it does not rerun tests.
- Selected handoffs must contain a frozen `enforce_plan` and ready `ci_facts_contract`.
- If selected handoffs contain `green` or `merged` tests, the CI facts file named by `ci_facts_contract.path` is required and must include exactly one result for each such test id.
- Approved artifacts are not rewritten to pass a PR.
- Every resolved finding must have a deterministic fingerprint in `feedback.json`.
- Every resolved finding must also have a `class_key`; fix handoffs require class sweep evidence.
- Re-enforce rounds must update `/tmp/eg/<run-id>/finding-ledger.json` before reporting.
- One user request runs one review round. Maximum three rounds per task.

## Workflow

At start, state `round N/3`.

Use one enforce run dir for the whole review/fix loop:

- first round: create `/tmp/eg/<run-id>/`
- fix handoff, closure evidence, and later rounds reuse the same `/tmp/eg/<run-id>/`
- do not start a new run dir for round 2/3, or lifecycle history is lost

Start completion criterion: either an existing enforce run dir is reused with its `finding-ledger.json`, or a new run dir is created for round 1 before selection starts.

1. Gather PR context with `"$SKILL_DIR/scripts/pr-context.sh"` when needed.
2. Select active handoffs:

```bash
python3 "$SKILL_DIR/scripts/select-handoffs.py" \
  --repo-root <repo> \
  --pr-context <pr-context.json> \
  --out /tmp/eg/<run-id>/selected_handoffs.json
```

3. Select Layer A quality context:

```bash
python3 "$SKILL_DIR/scripts/select-quality-context.py" \
  --diff <diff.patch> \
  --repo-root <repo> \
  --out /tmp/eg/<run-id>/quality-context.json
```

4. Run reviewers in parallel with fresh context and write:
   - `/tmp/eg/<run-id>/layer-a-findings.json`
   - `/tmp/eg/<run-id>/layer-b-findings.json`

Reviewer JSON must match `findings.schema.json`. If schema is invalid, fix reviewer JSON and rerun `enforce.py`; do not change product code for schema errors.

Review inputs:
   - Layer A: PR diff + quality protocol/rules + selected rule packs.
   - Layer B: PR diff + artifact protocol + ADR/BDD/CONTEXT + selected handoffs.
5. Resolve gate:

Read `CI-FACTS-FORMAT.md` before supplying `--facts`.

```bash
python3 "$SKILL_DIR/scripts/enforce.py" \
  --findings /tmp/eg/<run-id>/layer-a-findings.json \
  --findings /tmp/eg/<run-id>/layer-b-findings.json \
  --facts <ci-facts.json> \
  --handoffs /tmp/eg/<run-id>/selected_handoffs.json \
  --profile <enforcement.yml> \
  --artifacts-root <repo> \
  --out /tmp/eg/<run-id>/feedback.json
```

6. Update finding lifecycle ledger:

```bash
python3 "$SKILL_DIR/scripts/update-finding-ledger.py" \
  --feedback /tmp/eg/<run-id>/feedback.json \
  --closure-evidence /tmp/eg/<run-id>/closure-evidence.json \
  --out /tmp/eg/<run-id>/finding-ledger.json
```

Omit `--closure-evidence` when no fix agent has run yet. Omit `--round`; the script derives the next round from the existing ledger and rejects rounds after 3.

Exit handling:

- `select-handoffs.py` exit 1: no active handoff; stop and ask whether to return to `eg-tdd`.
- any script exit 2: contract/input error; stop and report the exact missing or invalid input.
- `enforce.py` exit 1: gate is blocked, not a script failure; continue to update finding ledger and report.
- `enforce.py` exit 0: continue to update finding ledger and report.

7. Notify human best-effort with `"$SKILL_DIR/scripts/notify.py"`; pass `--ledger /tmp/eg/<run-id>/finding-ledger.json` when available.
8. Report summary and ask one next question.

Round completion criterion: the run stops only after a contract error is reported, or after `feedback.json` and `finding-ledger.json` both exist and the summary asks exactly one next question.

## Round Summary

Report:

- gate and merge blocked status
- lifecycle buckets first: regression, partial-fix, persisted, new, closed
- blocking findings grouped by next action
- human decisions
- agent-fixable findings
- manual QA items
- residual risks or missing inputs

Missing or duplicate CI facts are contract errors, not findings. Stop and report the input problem.

Ask exactly one next question:

1. Human decision if any exists.
2. Else ask whether to generate `/tmp/eg/<run-id>/fix-handoff.md` for open agent-fixable ledger findings.
3. Else ask whether to prepare manual QA checklist.
4. Else report pass/no action.

If the user approves fix handoff, generate it from the ledger:

```bash
python3 "$SKILL_DIR/scripts/write-fix-handoff.py" \
  --ledger /tmp/eg/<run-id>/finding-ledger.json \
  --repo-root <repo> \
  --pr-context /tmp/eg/<run-id>/pr-context.json \
  --diff /tmp/eg/<run-id>/diff.patch \
  --handoffs /tmp/eg/<run-id>/selected_handoffs.json \
  --feedback /tmp/eg/<run-id>/feedback.json \
  --out /tmp/eg/<run-id>/fix-handoff.md
```

Then invoke `handoff` only if conversation context must be compacted for another agent. The generated file is the source of truth and must include closure evidence requirements and class sweep scope. The fix agent must write `/tmp/eg/<run-id>/closure-evidence.json`, verify, auto-commit only fix-scope files, run `"$SKILL_DIR/scripts/validate-fix-commit-scope.py"`, and stop if the fix requires changing approved ADR/BDD substance.

Then stop. Do not fix, rerun, apply overrides, update artifacts, or start another round unless the user asks.
