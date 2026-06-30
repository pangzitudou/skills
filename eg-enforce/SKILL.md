---
name: eg-enforce
description: "EG enforce stage: PR gate from handoffs, CI facts, isolated reviews, lifecycle ledger, and one next question."
disable-model-invocation: true
---

# eg-enforce

Run the PR-time EG outer loop. Report gate and ask one next question. Do not fix code.

The `eg` CLI wraps the gate pipeline and guards reviewer findings. `enforce.py`
alone assigns enforcement level, next step, and gate — you never judge the gate.
You run the isolated reviewers and supply CI facts. Run `eg schema findings` for
the findings format instead of reading the schema file.

```bash
EG="python3 $(readlink -f .agents/skills/eg)/cli/eg.py"
```

Read reviewer-judgment references for the layer you are running:

- `QUALITY-REVIEW.md`, `QUALITY-RULES.md` (Layer A)
- `ARTIFACT-REVIEW.md` (Layer B)
- `FINDING-LIFECYCLE.md`, `CI-FACTS-FORMAT.md`
- Shared method: `../eg/references/METHOD.md`, `ARTIFACT-MODEL.md`, `STAGE-HANDOFF.md`

## Invariants

- Reviewers identify findings only. `eg enforce` (enforce.py) assigns enforcement level, next step, waiver consumption, and gate.
- Enforcement level never comes from artifacts, CI, handoff, or reviewers.
- Reviewers are isolated. Do not pass conversation history, implementer rationale, or the ledger into reviewer subagents.
- CI owns test execution. This skill reads CI facts; it does not rerun tests.
- Approved artifacts are not rewritten to pass a PR.
- One user request runs one review round. Maximum three rounds per task.

## Workflow

State `round N/3` at start. Reuse one run dir for the whole review/fix loop.

1. Create the run and gather PR context:

```bash
$EG new enforce --repo-root <repo-root> --repo <name> --target <branch> [--source <branch>]
$EG pr-context <run>          # writes diff.patch + pr-context.json
```

2. Select active handoffs and quality context:

```bash
$EG select <run>             # selected_handoffs.json + quality-context.json
```

3. Run reviewers in parallel with **fresh context**, each writing its findings JSON into the run dir:
   - Layer A (`layer-a-findings.json`): PR diff + quality protocol/rules + selected rule packs.
   - Layer B (`layer-b-findings.json`): PR diff + artifact protocol + the repo's ADR/BDD/CONTEXT + selected handoffs.

   `eg schema findings` gives the shape. Guard them before the gate:

```bash
$EG check <run>              # rejects malformed / placeholder findings
```

4. Resolve the gate (reads CI facts; enforce.py owns the verdict; also updates the finding lifecycle ledger):

```bash
$EG enforce <run> --facts <ci-facts.json>
```

`eg enforce` exit 1 means the gate is blocked (a valid result), exit 2 means a contract/input error — stop and report the exact missing input (e.g. a missing or duplicate CI fact).

5. Notify best-effort and report:

```bash
$EG notify <run>             # dry-run digest by default; --send to deliver
```

## Round Summary

Report:

- gate and merge-blocked status
- lifecycle buckets first: regression, partial-fix, persisted, new, closed
- blocking findings grouped by next action
- human decisions, agent-fixable findings, manual QA items
- residual risks or missing inputs

Missing or duplicate CI facts are contract errors, not findings. Stop and report the input problem.

## One Next Question

Ask exactly one, by priority:

1. Human decision if any exists.
2. Else whether to generate the fix handoff for open agent-fixable findings.
3. Else whether to prepare a manual QA checklist.
4. Else report pass / no action.

If the user approves the fix handoff, generate it from the ledger:

```bash
$EG fix-handoff <run>        # -> fix-handoff.md from finding-ledger.json
```

The generated file is the source of truth; it carries fingerprints, closure
requirements, and class-sweep scope. The fix agent must write
`closure-evidence.json`, verify, auto-commit only fix-scope files, and stop if a
fix requires changing approved ADR/BDD substance. The next round consumes the
closure evidence.

Then stop. Do not fix, rerun, apply overrides, update artifacts, or start another round unless the user asks.
