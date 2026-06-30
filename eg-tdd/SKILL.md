---
name: eg-tdd
description: "EG TDD stage: approved intent -> approved BDD -> tests -> implementation -> handoff -> scoped commit."
disable-model-invocation: true
---

# eg-tdd

Turn approved intent into approved BDD, verified tests, minimal implementation, repo handoff, and commit.

The `eg` CLI owns BDD format, scaffolding, the BDD completeness gate, and wraps
the ledger/freeze/handoff validators. You own the grilling, the four-question
ruler, the adversarial hypotheses, and writing the actual tests and code. Author
BDD as data; do not hand-write `.md`. Run `eg schema bdd` when unsure of fields.

```bash
EG="python3 $(readlink -f .agents/skills/eg)/cli/eg.py"
```

Read judgment references for the current branch (format is in the CLI):

- BDD meaning ruler: `BDD-FORMAT.md` (questions ①②④ — observability, readability, implementation-independence)
- Handoff contract: `HANDOFF-FORMAT.md`
- Shared method: `../eg/references/METHOD.md`, `ARTIFACT-MODEL.md`, `STAGE-HANDOFF.md`

## Storage

BDD is authored as data under `/tmp/eg/<run>/`; `eg seal` commits the **data**
`docs/bdd/NNNN-slug.yml` (source of truth) and renders a git-ignored `.md` for
the legacy readers. `eg govern` / `eg commit-check` regenerate the `.md` from the
committed `.yml` first, so no reader is migrated. The ledger stays JSON machine
state; `freeze` / `govern` / `commit-check` wrap the existing validators. When
you fill the ledger's `touched_files` for the commit, list the committed `.yml`
(e.g. `docs/bdd/NNNN-slug.yml`), not the rendered `.md`.

## Required Start

Input must include exactly one active intent ADR with `type: intent`,
`status: review` or `approved`, and an Acceptance Criteria Seed. If missing or
only a decision ADR exists, stop and return to `eg-precipitate`. BDD must derive
from an intent ADR.

```bash
$EG new tdd --repo-root <repo-root> --task <task-slug> --intent-adr ADR-NNNN --mode lite
```

Use `--mode full` for bug fixes, permissions, idempotency/retry, concurrency,
transactions, database changes, external contracts, webhooks, async work, or
cross-module orchestration.

## Gate 1: BDD Approval

1. Read the intent ADR, related decision/constraint ADRs, and `CONTEXT.md`.
2. Draft BDD. For **every** Acceptance Criteria Seed item, derive at least one happy AND at least one edge/negative scenario:

```bash
$EG bdd-new <run> --title "<feature>" --derived-from ADR-NNNN
cat <<'YAML' | $EG merge <run> bdd-0001
scenarios:
  scenario-<slug>:
    title: "<scenario title>"
    kind: happy            # happy | edge
    given: ["<precondition>"]
    when:  ["<action>"]
    then:  ["<observable outcome>"]
YAML
```

3. `eg check <run> bdd-NNNN` enforces the countable rules (each scenario has Given/When/Then; at least one happy AND one edge; `derived_from` resolves to an intent ADR). Then apply the meaning ruler yourself: is `Then` observable, can business read it, would it hold under a different implementation? Rewrite until it passes both.
4. Preview and get human approval:

```bash
$EG render <run> bdd-0001     # human-readable preview, no repo write
```

5. On explicit approval, set status and seal (renders to `docs/bdd/`, stamps approval metadata):

```bash
$EG set  <run> bdd-0001 status approved
$EG seal <run> bdd-0001
```

Never seal/approve BDD before the human approves. Keep `draft` until then.

6. Freeze the enforce baseline immediately after approval. Author the frozen inputs into the ledger, then freeze:

```bash
cat <<'YAML' | $EG merge <run> ledger
intent: { id: ADR-NNNN, status: approved }
bdd: [ { id: BDD-0001, status: approved } ]
related_adrs: [ { id: ADR-NNNN, type: intent, status: approved } ]
enforce_plan:
  required_acceptance_tests:
    - { id: AT-001, derived_from: "BDD-0001#scenario-<slug>", expectation: "<observable>" }
  expected_adversarial_domains: []
  manual_qa_expected: []
  out_of_scope: []
  nfr_checkpoints: []
ci_facts_contract: { producer: "<CI job/command>", path: "ci-facts.json" }
YAML
$EG freeze <run>          # writes enforce-plan.yml + ci-facts.contract.json + frozen hash
```

## Gate 2: Tests, Implementation, Handoff

1. Complete the ledger: `adr_coverage` (every related ADR `covered`/`not-applicable`/`deferred`), and `ci_facts_contract.expected_acceptance_test_ids` matching the frozen plan.
2. Validate planning:

```bash
$EG govern <run> --phase planning
```

3. Write acceptance tests first. Each test id must appear in the real test name and derive from a BDD scenario. Confirm RED fails for the intended behavior.
4. Generate adversarial hypotheses before non-AT tests. Expected outcomes must cite BDD, spec, ADR, requirement, or contract — never an implementation-only oracle. Drive RED -> GREEN -> sensitivity review.
5. Before final validation, set in the ledger:
   - `ci_facts_contract.status: ready`
   - `ci_facts_contract.required_result_ids`: exactly every `AT-*`/`H*` with status `green` or `merged`.
6. Validate final and emit the handoff:

```bash
$EG govern <run> --phase final --emit-handoff      # -> <repo>/.eg/handoff/<run-id>.yml
```

7. Commit only this run's files. Stage code, tests, BDD/ADR status changes, and the handoff, then:

```bash
$EG commit-check <run> --handoff .eg/handoff/<run-id>.yml
git commit -m "..."        # include Intent, BDD, and Run in the message
```

Stop if related files overlap unrelated dirty changes. Never commit `/tmp/eg`.

## Never

- Invent business intent.
- Derive BDD from a decision ADR.
- Seal/approve BDD before human approval, or write tests against draft BDD.
- Edit approved ADR/BDD substance to make code pass.
- Let implementation define the assertion oracle.
- Emit enforcement level or gate judgment — that is `eg-enforce` only.
