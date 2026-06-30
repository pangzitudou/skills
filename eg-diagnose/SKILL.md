---
name: eg-diagnose
description: "EG diagnosis stage: evidence-backed root cause artifacts in /tmp/eg, no code or repo edits."
disable-model-invocation: true
---

# eg-diagnose

Find root causes with evidence before EG precipitation. Do not edit code, repo artifacts, data, config, cache, indexes, or commits.

The `eg` CLI owns artifact format, scaffolding, validation, and the completeness
gate. You supply the semantics; the CLI keeps the structure correct. Do not
hand-write `/tmp/eg` artifacts and do not read format docs to learn field
shapes — run `eg schema <artifact>` when unsure.

```bash
EG="python3 $(readlink -f .agents/skills/eg)/cli/eg.py"
```

Read shared method only when you need the contract: `../eg/references/METHOD.md`,
`ARTIFACT-MODEL.md`, `STAGE-HANDOFF.md`. Format lives in the CLI, not in docs.

## Write contract

- `eg merge <run> <artifact>` — fold a YAML fragment (stdin) into one artifact. Keyed lists (`categories`, `symptoms`, `problem_findings`, `root_causes`, `fix_options`, evidence) accept a map keyed by id; the CLI fills structure, validates, and rejects placeholders. This is the workhorse — one fragment, one call.
- `eg set <run> <artifact> <path> <value>` — single scalar tweak, e.g. `eg set $RUN source-gap status complete`.
- Unknown yet? Use `defer: <reason>` as the value. A silent `TBD`/empty is rejected; an explicit deferral passes and is surfaced by `eg check`.
- `eg schema <artifact>` — fields, required leaves, and enums on demand.

Artifacts: `source-matrix` `source-gap` `query-plan` `diagnosis`.

## Workflow

1. Create the run:

```bash
$EG new diagnosis --repo <repo-name> --task <task-slug>
```

Use the printed run id/path as `<run>` below.

2. Triage scan. Read relevant code and existing governance. Identify symptoms and suspected surfaces. Infer which source categories you need. List hypotheses only; do not claim root cause yet. Record symptoms and the source matrix:

```bash
cat <<'YAML' | $EG merge <run> diagnosis
symptoms:
  S1: { description: "<observable symptom>", status: explained }
YAML

cat <<'YAML' | $EG merge <run> source-matrix
categories:
  code: { needed: true, reason: "<why>", impact_if_missing: "<impact>" }
  # ... every taxonomy category; mark needed true/false with a reason
YAML
```

Complete only when every symptom has a suspected surface and every category has an explicit `needed` + reason.

3. Source gap. One round at most. Set status and any questions:

```bash
$EG set <run> source-gap status complete   # or: degraded | blocked
```

If the user cannot provide missing critical sources and says continue, set `degraded` and add `degraded_reason`. If blocked, add `questions_for_user`.

4. Query plan before any external query. Read-only queries may run only after the plan is written:

```bash
cat <<'YAML' | $EG merge <run> query-plan
queries:
  Q1: { source: "<db|log|es|http>", purpose: "<prove/rule out>", operation: SELECT, risk: low, expected_evidence: "<what>" }
YAML
```

Never perform side-effecting, notifying, mutating, or cost-incurring operations. If one is required, stop and ask the user to authorize it outside diagnosis.

5. Deep diagnosis. Track each symptom independently. Store raw sensitive source material only under `<run>/sources/`; keep derived artifacts redacted. Distinguish `root_cause`, `probable_root_cause`, `hypothesis`. Record findings, evidence, and fix options:

```bash
cat <<'YAML' | $EG merge <run> diagnosis
root_causes:
  RC1: { finding_type: root_cause, confidence: high, explains: [S1], summary: "<cause>", evidence: { E1: { source_type: runtime_behavior, source_ref: "<ref>", strength: direct, summary: "<obs>" } } }
problem_findings:
  P1: { symptom: S1, problem: "<user-facing problem>", status: explained, finding_type: root_cause, confidence: high, root_cause: "<cause for this problem>", cause_refs: [RC1], evidence: { E1: { source_type: runtime_behavior, source_ref: "<ref>", strength: direct, summary: "<obs>" } }, missing_evidence: [], fix_options: [F1] }
fix_options:
  F1: { addresses: [RC1], summary: "<fix direction>", expected_effect: [S1], risks: [], required_validation: [], needs_precipitation: true }
YAML
```

`problem_findings` must have exactly one entry per symptom, each with its own root cause and evidence.

6. Check until green. `eg check` reports gaps and deferrals; it is the gate's pre-flight:

```bash
$EG check <run>
```

7. Seal. The hard gate: it refuses unless `eg check` passes, then marks the diagnosis `diagnosis-complete` and renders `diagnosis-preview.md`:

```bash
$EG seal <run>
```

Do not declare diagnosis complete unless `eg seal` succeeded.

## Evidence Gate

- `root_cause + high`: requires direct evidence or at least two independent supporting source types, and a `complete` source gap.
- `probable_root_cause`: strong evidence but missing runtime/data/reproduction/config evidence.
- `hypothesis`: reasoning only or insufficient direct evidence.

The CLI enforces these as countable rules. You still judge whether the evidence genuinely supports the cause.

## Query Boundary

Allowed after the query plan exists:

- local code read/search
- `SELECT`, `SHOW`, `DESCRIBE`, `EXPLAIN`
- ES/log search
- HTTP GET
- browser/network inspection without submitting forms

Not allowed in diagnose:

- HTTP POST/PUT/PATCH/DELETE
- sending code/email/SMS/webhook
- DB/cache/index mutation
- migration or DDL
- scripts with side effects
- anything that can notify users, change state, or cost money

## Output

End with:

- diagnosis status (sealed or blocked, from `eg seal`/`eg check`)
- problem-by-problem findings; each problem contains its own root cause and evidence
- missing evidence and any deferrals
- fix options
- one question: whether to enter `eg-precipitate`

Do not write ADR, BDD, CONTEXT, `.eg/handoff`, or code.
