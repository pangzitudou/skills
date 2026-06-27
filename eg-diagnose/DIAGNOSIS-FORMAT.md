# Diagnosis Format

All diagnosis artifacts live under `/tmp/eg/<run-id>/`.

Allowed derived artifacts:

```text
source-matrix.yml
source-gap.yml
query-plan.yml
diagnosis.yml
diagnosis-preview.md
```

Raw sensitive material may live only under:

```text
sources/
```

Do not copy raw source material into repo artifacts or precipitation artifacts.

## diagnosis.yml

```yaml
schema: eg-diagnosis/v1
run_id: EG-RUN-...
stage: diagnosis-complete
repo: repo-name
task: task-slug
created_at: 2026-06-27T00:00:00Z
source_matrix: /tmp/eg/EG-RUN-.../source-matrix.yml
source_gap: /tmp/eg/EG-RUN-.../source-gap.yml
query_plan: /tmp/eg/EG-RUN-.../query-plan.yml
sensitive_material:
  stored_locally: true
  paths:
    - /tmp/eg/EG-RUN-.../sources/Q1.raw.json
  do_not_copy_to_repo: true
symptoms:
  - id: S1
    description: ...
    status: explained
problem_findings:
  - id: P1
    symptom: S1
    problem: ...
    status: explained
    finding_type: root_cause
    confidence: high
    root_cause: ...
    cause_refs: [RC1]
    evidence:
      - id: E1
        source_type: runtime_behavior
        source_ref: /tmp/eg/EG-RUN-.../sources/Q1.summary.yml
        strength: direct
        summary: ...
    missing_evidence: []
    fix_options: [F1]
root_causes:
  - id: RC1
    finding_type: root_cause
    confidence: high
    explains: [S1]
    summary: ...
    evidence:
      - id: E1
        source_type: runtime_behavior
        source_ref: /tmp/eg/EG-RUN-.../sources/Q1.summary.yml
        strength: direct
        summary: ...
    ruled_out: []
unexplained_symptoms: []
fix_options:
  - id: F1
    addresses: [RC1]
    summary: ...
    expected_effect: [S1]
    risks: []
    required_validation: []
    needs_precipitation: true
handoff_to_precipitate:
  proposed_intents:
    - id: PI1
      based_on:
        root_causes: [RC1]
        fix_options: [F1]
      summary: ...
      acceptance_seed_candidates: []
      decisions_needed: []
      constraints_to_check: []
```

## Evidence Levels

- `root_cause + high`: direct evidence, or at least two independent supporting source types.
- `probable_root_cause + medium`: strong evidence but missing runtime/data/reproduction/config proof.
- `hypothesis + low`: plausible reasoning without enough direct evidence.

## Problem Findings

`problem_findings[]` is the human-facing diagnosis. It must have exactly one item per `symptoms[]` item.

Each item must contain:

- `problem`: the user-facing problem text, not a shortened category.
- `root_cause`: the diagnosis for that problem only.
- `evidence`: the evidence for that problem only.
- `missing_evidence`: named gaps for that problem.
- `fix_options`: fix option ids that address that problem.

Do not output a separated global "root cause" section followed by a separated global "evidence" section. In `diagnosis-preview.md`, render by problem:

```md
## 分析结果

### P1: {problem}
- 状态: {status} / {finding_type} / {confidence}
- 根因: {root_cause}
- 依据:
  - {source_ref}: {summary}
- 缺口: {missing_evidence or none}
- 修复方向: {fix_options}
```

If one underlying cause explains several problems, repeat the cause summary under each affected problem and cite the evidence relevant to that problem. The shared cause may also appear once in `root_causes[]`, but it does not replace per-problem evidence.

`root_causes[].explains` must reference `symptoms[].id`.

`unexplained_symptoms[]` must reference symptoms without enough evidence.

`fix_options[].addresses` must reference finding ids.

`handoff_to_precipitate` is only a proposal. `eg-precipitate` must grill before writing repo artifacts.
