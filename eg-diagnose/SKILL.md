---
name: eg-diagnose
description: EG diagnosis stage: evidence-backed root cause artifacts in /tmp/eg, no code or repo edits.
disable-model-invocation: true
---

# eg-diagnose

Find root causes with evidence before EG precipitation. Do not edit code, repo artifacts, data, config, cache, indexes, or commits.

Set:

```bash
SKILL_DIR="$(readlink -f .agents/skills/eg-diagnose)"
```

Shared references:

- `../eg/references/METHOD.md`
- `../eg/references/ARTIFACT-MODEL.md`
- `../eg/references/STAGE-HANDOFF.md`

Local references:

- Read `SOURCE-TAXONOMY.md` before writing `source-matrix.yml`.
- Read `DIAGNOSIS-FORMAT.md` before writing `diagnosis.yml`.

## Workflow

1. Create runtime state:

```bash
python3 "$SKILL_DIR/scripts/new-diagnosis.py" --repo <repo-name> --task <task-slug>
```

2. Triage scan:
   - Read relevant code and existing governance.
   - Identify symptoms and suspected surfaces.
   - Infer needed source categories.
   - List initial hypotheses only. Do not claim root cause.
   - Complete only when every symptom has at least one suspected surface and needed source category.

3. Write `/tmp/eg/<run-id>/source-matrix.yml`.
   - Include every taxonomy category.
   - For every category, set `needed: true|false`.
   - Always give `reason` and `impact_if_missing`.
   - Complete only when missing critical categories are visible to the user.

4. Write `/tmp/eg/<run-id>/source-gap.yml`.
   - Ask at most one concrete source-gap question round.
   - If the user cannot provide missing critical sources and says continue, set status `degraded`.
   - Complete only when status is `complete`, `degraded`, or `blocked`.

5. Before external queries, write `/tmp/eg/<run-id>/query-plan.yml`.
   - Read-only queries may run after the plan is written.
   - Never perform side-effecting, notifying, mutating, or cost-incurring operations in diagnose. If such an action is required to continue, stop and ask the user to authorize it outside diagnosis.

6. Deep diagnosis:
   - Track each symptom independently.
   - Store raw sensitive source material only under `/tmp/eg/<run-id>/sources/`.
   - Keep derived artifacts redacted.
   - Distinguish `root_cause`, `probable_root_cause`, and `hypothesis`.
   - Complete only when every symptom has exactly one `problem_findings[]` entry with its own root cause, evidence, missing evidence, and fix option refs.

7. Write `/tmp/eg/<run-id>/diagnosis.yml`, then render `/tmp/eg/<run-id>/diagnosis-preview.md`:

```bash
python3 "$SKILL_DIR/scripts/render-diagnosis-preview.py" /tmp/eg/<run-id>/diagnosis.yml
```

   - For each user problem, show: status, root cause, evidence bullets, missing evidence, fix direction.
   - Do not hand-write a separated global root-cause section followed by a separated global evidence section.

8. Validate before declaring completion:

```bash
python3 "$SKILL_DIR/scripts/validate-diagnosis.py" /tmp/eg/<run-id>/diagnosis.yml
```

If validation fails, do not say diagnosis is complete. Report blocking gaps and next source requests.

## Evidence Gate

- `root_cause + high`: requires direct evidence or at least two independent supporting source types.
- `probable_root_cause`: strong evidence but missing runtime/data/reproduction/config evidence.
- `hypothesis`: reasoning only or insufficient direct evidence.
- Missing `source-matrix.yml` or `source-gap.yml` forbids completed root-cause output.

## Query Boundary

Allowed after `query-plan.yml`:

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

- diagnosis status
- problem-by-problem findings; each problem contains its own root cause and evidence
- missing evidence
- fix options
- one question: whether to enter `eg-precipitate`

Do not write ADR, BDD, CONTEXT, `.eg/handoff`, or code.
