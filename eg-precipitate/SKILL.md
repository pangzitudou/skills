---
name: eg-precipitate
description: "EG precipitation stage: grill intent, scope, terms, decisions, and constraints into CONTEXT/ADR artifacts."
disable-model-invocation: true
---

# eg-precipitate

Make intent governable. Do not implement, write BDD, run tests, or enforce gates.

The `eg` CLI owns ADR/CONTEXT format, scaffolding, validation, and the seal gate.
You own the grilling and the semantics. Author artifacts as structured data; do
not hand-write `.md`, and do not read format docs to learn field shapes — run
`eg schema <kind>` when unsure.

```bash
EG="python3 $(readlink -f .agents/skills/eg)/cli/eg.py"
```

Read judgment references for the current branch (format is in the CLI, not docs):

- Interaction and decision-tree pressure: `references/interaction-protocol.md`
- Artifact eligibility: `references/precipitation-triggers.md`
- NFR checkpoint: `references/nfr-checklist.md`
- Failure modes: `references/failure-modes.md`
- Shared method: `../eg/references/METHOD.md`, `STAGE-HANDOFF.md`

## Storage

You author ADR/CONTEXT as data under `/tmp/eg/<run>/`. `eg seal` commits the
**data** as the source of truth — `docs/adr/NNNN-slug.yml`, `CONTEXT.yml` — and
renders a git-ignored `.md` beside it for humans and the legacy `.md` readers
(it refuses unless validation passes). The rendered `.md` is regenerated on
demand (`eg render-all <repo>`), never committed. Commit the `.yml`, not the `.md`.

## Write contract

- `eg adr-new <run> --type intent|decision|constraint --title "..." [--domain ...]` — reserve the next ADR number and scaffold its data.
- `eg merge <run> <artifact>` — fold a YAML fragment (stdin) into `context` or `adr-NNNN`. One fragment, one call.
- `eg set <run> <artifact> <path> <value>` — single scalar tweak (e.g. `eg set <run> adr-0001 status approved`).
- Unknown yet? Use `defer: <reason>`. Silent `TBD`/empty is rejected.
- `eg check <run> [artifact]` — gaps + deferrals. `eg render <run> <artifact>` — human preview without touching the repo. `eg schema context|adr-intent|adr-decision|adr-constraint` — fields and enums.

## Loop

Walk the decision tree one branch at a time until a conclusion is stable enough
to govern future work. Use the per-turn shape in `interaction-protocol.md`: state
the decision in plain language, recommend an answer, ask one hard question. If
code or existing artifacts can answer it, inspect them instead of asking.

A branch is resolved only when it has an explicit term, scope boundary, decision,
constraint, non-goal, or defer reason. A plausible answer is not enough.

## Workflow

1. Create the run:

```bash
$EG new precipitate --repo-root <repo-root> --task <task-slug>
```

2. Grill. Default to not writing. Inspect existing `CONTEXT.md` and `docs/adr/` first.

3. Write when stable, after a one-step preview + user confirmation:

- Term resolved → `eg merge <run> context` (name, description, terms).
- Business scope confirmed → `eg adr-new <run> --type intent --title "..."`, then merge `context`, `decision`, `in_scope`, `out_of_scope`, `non_goals`, and `acceptance_seed`.
- Hard-to-reverse choice with real tradeoffs → `--type decision`.
- Confirmed NFR → `--type constraint --domain <domain>`.

```bash
$EG adr-new <run> --type intent --title "Reset Password Flow"
cat <<'YAML' | $EG merge <run> adr-0001
context: "<why this came up>"
decision: "<agreed scope>"
in_scope: ["<capability>"]
out_of_scope: ["<deferred neighbour>"]
non_goals: ["<explicitly rejected>"]
acceptance_seed: ["<observable outcome for later BDD>"]
YAML
```

4. Before closing an intent ADR, ask the NFR checklist once (`nfr-checklist.md`). Each confirmed item becomes a `constraint` ADR.

5. Check and seal each artifact. `eg seal` is the hard gate — it renders to the repo only if the data check AND the original ADR validator pass:

```bash
$EG check <run> adr-0001
$EG seal  <run> adr-0001     # -> docs/adr/0001-...md
```

## Intent Approval Gate

Keep intent ADR `status: review` until the user approves. Only `eg-tdd` consumes
an approved intent with an Acceptance Criteria Seed. On approval:

```bash
$EG set  <run> adr-0001 status approved
$EG seal <run> adr-0001     # seal enforces the seed for approved intent
```

If the user is not ready, keep `review`; `eg-tdd` may only draft/preview BDD.

## Artifact Rules

- `CONTEXT`: durable project language only — terms, definitions, rejected synonyms. No scope, decisions, or constraints.
- Intent ADR: business scope (`In/Out/Non Goals`) and Acceptance Criteria Seed. Only intent ADRs seed BDD.
- Decision ADR: hard-to-reverse choices with tradeoffs. Never seeds BDD.
- Constraint ADR: explicit NFR with `domain`.

The CLI enforces the countable structure (scope triple present, seed present for
approved intent, no BDD in an ADR). You judge whether In Scope is a real boundary
and whether Out of Scope pins the high-drift neighbours.

## Closing

Summarize only:

- terms and ADRs sealed to the repo
- intent ADRs approved and ready for BDD derivation
- decision ADRs and constraint ADRs with domains
- unresolved branches
- next stage, usually `eg-tdd`

Do not write BDD, run tests, enforce gates, or rewrite approved ADR substance.
