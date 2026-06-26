# EG Artifact Model

## Repo Artifacts

```text
CONTEXT.md
docs/adr/*.md
docs/bdd/*.md
.eg/handoff/<run-id>.yml
```

Repo artifacts are stable and reviewable. `.eg/handoff/*.yml` is the only authoritative traceability handoff for `eg-enforce`.

Deprecated:

```text
traceability.yml
```

## Runtime Artifacts

```text
/tmp/eg/<run-id>/ledger.json
/tmp/eg/<run-id>/notes.md
/tmp/eg/<run-id>/selected_handoffs.json
/tmp/eg/<run-id>/feedback.json
/tmp/eg/<run-id>/fix-handoff.md
```

Runtime artifacts are not committed.

## BDD Approval Metadata

Approved BDD frontmatter must include:

```yaml
id: BDD-0001
status: approved
derived_from: ADR-0001
approved_by: human
approved_at: 2026-06-26T11:30:00+08:00
approval_source: chat-confirmation
```

## Ledger

`/tmp/eg/<run-id>/ledger.json` is strict machine state. Freeform notes belong in `notes.md`.

Required root shape:

```json
{
  "schema": "eg-ledger/v1",
  "run_id": "EG-RUN-20260626-xxxx",
  "stage": "tdd",
  "repo": "repo-name",
  "task": "task-slug",
  "mode": "lite",
  "intent": {"id": "ADR-0001", "status": "approved"},
  "bdd": [{"id": "BDD-0001", "status": "approved"}],
  "related_adrs": [],
  "adr_coverage": [],
  "context_read": [],
  "unknowns": [],
  "acceptance_tests": [],
  "hypotheses": [],
  "cycles": [],
  "sensitivity": [],
  "manual_qa": [],
  "touched_files": []
}
```

## Handoff

Repo handoff shape:

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
  - id: ADR-0002
    type: constraint
    status: approved
adr_coverage:
  - adr: ADR-0001
    coverage: covered
    covered_by:
      - BDD-0001#scenario-x
      - AT-001
    reason: intent behavior covered by approved BDD and acceptance test
  - adr: ADR-0002
    coverage: covered
    covered_by:
      - H1
    reason: security constraint covered by internal hypothesis
tests:
  - id: AT-001
    name: "AT-001 observable behavior"
    derived_from: BDD-0001#scenario-x
    artifact_status: approved
    status: green
  - id: H1
    name: "H1 internal invariant"
    derived_from: internal
    source: ADR-0002
    artifact_status: approved
    status: green
manual_qa: []
tmp_run_dir: /tmp/eg/EG-RUN-20260626-xxxx
tmp_run_dir_authoritative: false
```

Do not include `commit`. `eg-enforce` derives the touched commit from git.

## ADR Coverage

Every related ADR must be classified:

```text
covered
not-applicable
deferred
```

Rules:

- `intent`: must be `covered` by at least one BDD scenario and one AT.
- `constraint`: covered by `H*` or `manual_qa:*`, unless `not-applicable` or `deferred` with reason.
- `decision`: may be `covered`, `not-applicable`, or `deferred`; absent is invalid.
- `covered_by` may reference `BDD-NNN#scenario-x`, `AT-NNN`, `HNN`, or `manual_qa:<id>`.
- Code paths are evidence, not coverage proof.
