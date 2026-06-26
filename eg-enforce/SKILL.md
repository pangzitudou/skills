---
name: eg-enforce
description: PR-time Executable Governance gate. Select active .eg/handoff manifests from PR diff, read CI facts and artifacts, run isolated Layer A/B reviews, let scripts assign enforcement level/gate, and ask one next question. Use for EG review, merge readiness, PR gates, CI facts, handoff enforcement, or when eg-router routes to enforce.
---

# eg-enforce

Run the PR-time EG outer loop. Report gate and ask one next question. Do not fix code.

Shared references:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Local references:

- `QUALITY-REVIEW.md`
- `QUALITY-RULES.md`
- `ARTIFACT-REVIEW.md`
- `FINDING-LIFECYCLE.md`
- `enforcement.default.yml`
- `findings.schema.json`

## Invariants

- Reviewers identify findings only.
- `scripts/enforce.py` alone assigns enforcement level, next step, waiver consumption, and gate.
- Artifact status may enter enforcement. Enforcement level never comes from upstream artifacts, CI, handoff, or reviewers.
- Reviewers are isolated. Do not pass conversation history, implementer rationale, or `/tmp/eg` ledger into reviewer subagents.
- CI owns test execution. This skill reads CI facts; it does not rerun tests.
- If selected handoffs contain `green` or `merged` tests, `ci-facts.json` is required and must include exactly one result for each such test id.
- Approved artifacts are not rewritten to pass a PR.
- Every resolved finding must have a deterministic fingerprint in `feedback.json`.
- Re-enforce rounds must update `/tmp/eg/<run-id>/finding-ledger.json` before reporting.
- One user request runs one review round. Maximum three rounds per task.

## Workflow

At start, state `round N/3`.

1. Gather PR context with `scripts/pr-context.sh` when needed.
2. Select active handoffs:

```bash
python3 scripts/select-handoffs.py \
  --repo-root <repo> \
  --pr-context <pr-context.json> \
  --out /tmp/eg/<run-id>/selected_handoffs.json
```

3. Select Layer A quality context:

```bash
python3 scripts/select-quality-context.py \
  --diff <diff.patch> \
  --repo-root <repo> \
  --out /tmp/eg/<run-id>/quality-context.json
```

4. Run reviewers in parallel with fresh context:
   - Layer A: PR diff + quality protocol/rules + selected rule packs.
   - Layer B: PR diff + artifact protocol + ADR/BDD/CONTEXT + selected handoffs.
5. Resolve gate:

```bash
python3 scripts/enforce.py \
  --findings <layer-a.json> \
  --findings <layer-b.json> \
  --facts <ci-facts.json> \
  --handoffs /tmp/eg/<run-id>/selected_handoffs.json \
  --profile <enforcement.yml> \
  --artifacts-root <repo> \
  --out /tmp/eg/<run-id>/feedback.json
```

6. Update finding lifecycle ledger:

```bash
python3 scripts/update-finding-ledger.py \
  --feedback /tmp/eg/<run-id>/feedback.json \
  --closure-evidence /tmp/eg/<run-id>/closure-evidence.json \
  --round <N> \
  --out /tmp/eg/<run-id>/finding-ledger.json
```

Omit `--closure-evidence` when no fix agent has run yet.

7. Notify human best-effort with `scripts/notify.py`; pass `--ledger /tmp/eg/<run-id>/finding-ledger.json` when available.
8. Report summary and ask one next question.

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
python3 scripts/write-fix-handoff.py \
  --ledger /tmp/eg/<run-id>/finding-ledger.json \
  --out /tmp/eg/<run-id>/fix-handoff.md
```

Then invoke `handoff` only if conversation context must be compacted for another agent. The generated file is the source of truth and must include closure evidence requirements. The fix agent must write `/tmp/eg/<run-id>/closure-evidence.json`, verify, auto-commit only fix-scope files, and stop if the fix requires changing approved ADR/BDD substance.

Then stop. Do not fix, rerun, apply overrides, update artifacts, or start another round unless the user asks.
