# EG Handoff Format

`.eg/handoff/<run-id>.yml` replaces `traceability.yml`.

It is the repo-committed contract `eg-enforce` reads. It carries traceability, run identity, artifact statuses, and manual QA. It does not include `/tmp/eg` details beyond a non-authoritative debug path.

## Shape

```yaml
schema: eg-handoff/v1
run_id: EG-RUN-20260626-xxxx
stage: tdd-complete
repo: repo-name
agent: codex
intent:
  id: ADR-0001
  status: approved
bdd:
  - id: BDD-0001
    status: approved
related_adrs:
  - id: ADR-0001
    type: intent
    status: approved
adr_coverage:
  - adr: ADR-0001
    coverage: covered
    covered_by: [BDD-0001#scenario-neutral-response, AT-001]
    reason: intent behavior covered by BDD and acceptance test
tests:
  - id: AT-001
    name: "AT-001 neutral response"
    derived_from: BDD-0001#scenario-neutral-response
    artifact_status: approved
    status: green
  - id: H1
    name: "H1 idempotent replay"
    derived_from: internal
    source: ADR-0002
    artifact_status: approved
    status: green
manual_qa: []
tmp_run_dir: /tmp/eg/EG-RUN-20260626-xxxx
tmp_run_dir_authoritative: false
```

## Rules

- `tests[].id` must appear in the real test name.
- `derived_from` is a BDD scenario id or `internal`.
- `internal` requires `source`, usually a constraint ADR or spec.
- `artifact_status` is status only; enforcement level never appears here.
- Do not include `commit`; `eg-enforce` derives touched commit from git.
- Every `related_adrs[]` item must have an `adr_coverage[]` entry.
- `deferred` coverage is allowed, but `eg-enforce` surfaces it as a human decision.
