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
/tmp/eg/<run-id>/source-matrix.yml
/tmp/eg/<run-id>/source-gap.yml
/tmp/eg/<run-id>/query-plan.yml
/tmp/eg/<run-id>/diagnosis.yml
/tmp/eg/<run-id>/diagnosis-preview.md
/tmp/eg/<run-id>/sources/
/tmp/eg/<run-id>/enforce-plan.yml
/tmp/eg/<run-id>/ci-facts.contract.json
/tmp/eg/<run-id>/notes.md
/tmp/eg/<run-id>/selected_handoffs.json
/tmp/eg/<run-id>/feedback.json
/tmp/eg/<run-id>/fix-handoff.md
```

Runtime artifacts are not committed.

## Diagnosis

`eg-diagnose` writes only `/tmp/eg/<run-id>` artifacts. Raw source material,
including local sensitive material, may live only under `sources/`.

Derived diagnosis artifacts are redacted by default:

```text
source-matrix.yml
source-gap.yml
query-plan.yml
diagnosis.yml
diagnosis-preview.md
```

`diagnosis.yml` may hand off candidate intents and acceptance seeds to
`eg-precipitate`, but `eg-precipitate` must grill before writing repo artifacts.

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
    "enforce_plan": {},
    "ci_facts_contract": {},
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
enforce_plan:
  schema: eg-enforce-plan/v1
  status: frozen
  frozen_at: 2026-06-26T12:00:00+08:00
  source: bdd-approval
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
  required_acceptance_tests:
    - id: AT-001
      derived_from: BDD-0001#scenario-x
      expectation: observable behavior
  expected_adversarial_domains: [security]
  manual_qa_expected: []
  out_of_scope: []
  nfr_checkpoints: []
ci_facts_contract:
  schema: eg-ci-facts-contract/v1
  status: ready
  path: ci-facts.json
  producer: CI job or command that publishes ci-facts.json
  required_for_statuses: [green, merged]
  expected_acceptance_test_ids: [AT-001]
  required_result_ids: [AT-001, H1]
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

## Enforce Plan

`enforce_plan` freezes the review baseline immediately after BDD human approval.
Later TDD work may prove coverage or defer items with a reason, but may not
weaken required acceptance tests, related ADRs, out-of-scope boundaries, or NFR checkpoints.

## CI Facts Contract

`ci_facts_contract` declares the CI facts artifact before final handoff.

Rules:

- `path` names the CI artifact or file that `eg-enforce --facts` must receive.
- `producer` names the CI job or command responsible for publishing it.
- `expected_acceptance_test_ids` must match `enforce_plan.required_acceptance_tests`.
- `required_result_ids` must exactly match final handoff tests with `status: green` or `merged`.

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
