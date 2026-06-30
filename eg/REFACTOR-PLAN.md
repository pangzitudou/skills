# EG CLI Refactor Plan

Blueprint for collapsing the `eg-*` skill family onto a single executable governance CLI.
Source: grill session 2026-06-29.

## Problem

Two recurring pains across sessions:

1. **Emit cost.** The agent burns context authoring whole verbose YAML/JSON artifacts and reading format docs to learn field shapes before writing.
2. **Late omissions.** Missing fields and missing whole artifacts surface only at `eg-enforce`.

## Root Cause

Field knowledge is **triplicated**: scaffold scripts, validator scripts, and format docs each carry a private copy and drift apart.

Concrete symptom: `new-diagnosis.py` scaffolds `reason: "TBD"`; `validate-diagnosis.py` checks the field is *present and non-empty*; `"TBD"` passes. The omission is invisible until a human/enforce reviewer reads it.

Where omissions concentrate today: weakly-validated, placeholder-prone artifacts (source-matrix reasons, diagnosis/ADR/BDD/CONTEXT prose) plus `ci-facts.json` (inherently late — CI produces it at enforce). The strongly-validated cross-links in `validate-governance.py` (ci-facts AT ids ↔ enforce_plan, required_result_ids ↔ green tests) already work and must be preserved.

Fix: **one schema registry as the single source of truth; every action derives from it.** Both pains share this foundation.

## Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Omissions are **structural** (missing fields + missing whole files), not semantic judgment | Determines the CLI can actually fix them |
| 2 | Write contract: **`merge` primary** (one semantic fragment per artifact, one call), **`set` for scalar tweaks**, validate on write, reject silent `TBD` | Cuts emit cost and makes incompleteness visible at write-time |
| 3 | Maximize structuring: every artifact is a **data graph + prose leaves**; the structure line runs through fields, not files | User goal: precise updates |
| 4 | ADR/BDD/CONTEXT primary reader is the **agent** → **data is the source of truth**, not `.md` | Removes the prose-`.md` requirement |
| 5 | Human-readable `.md`: **data-only in repo, `eg render` on demand**; do not commit `.md` views | Fewest files, no desync; humans read only at the approval gate |
| 6 | Completeness gate: **hard gate + explicit `defer: <reason>` escape**; silent `TBD` = hard fail, `defer` passes | Incompleteness physically cannot cross a stage boundary, without deadlocking on legitimately-unknown items |
| 7 | CLI owns **countable completeness**; agent owns **meaning** | Machines enforce presence/structure; humans judge whether a `Then` is observable or an edge scenario is real |
| 8 | Form: **single python3 `eg` package + single schema registry**; `scaffold`/`merge`/`set`/`check`/`render` all derive from it | Roots out the triplication; stay on the existing toolchain |

## Target Architecture

```
schema registry  (single source of truth per artifact:
                  fields, required-ness, enums, defaults, "what counts as unfilled")
   ├─ eg new <artifact>          scaffold from registry; write null or omit, never "TBD"
   ├─ eg merge <run> <artifact>  fold a semantic fragment in; validate + reject unfilled   ← workhorse
   ├─ eg set <run> <path> <val>  single-scalar tweak; validate that field
   ├─ eg check <run>             per-stage required-artifact + required-field manifest
   │                             + cross-artifact links (AT→BDD scenario, ADR coverage, ci-facts ids)
   ├─ eg render <artifact>       on-demand human .md for the approval gate / PR
   ├─ eg schema <artifact>       on-demand field spec (replaces reading format docs)
   └─ eg freeze | handoff | enforce   existing logic, pulled under one entrypoint
```

**Hard gate:** the stage-advance / handoff-emit commands refuse unless `eg check` passes.

**Format knowledge moves into the CLI** (scaffold defaults + error messages + `eg schema`). The agent reads only judgment docs (METHOD invariants, interaction-protocol, the BDD four-question ruler's *meaning* questions, reviewer quality rules), and only on demand.

### Countable checks the CLI absorbs (`eg check`)

- Every Acceptance Criteria Seed → ≥1 happy AND ≥1 edge/negative scenario.
- Every NFR domain → answered or `defer`.
- Every related ADR → classified `covered` / `not-applicable` / `deferred`.
- Every symptom → exactly one `problem_findings` entry.
- No silent `TBD` / unfilled-without-defer anywhere.
- All existing `validate-governance.py` cross-links (preserve, do not weaken).

### Left to the agent / reviewer (meaning)

- Is the `Then` observable, not an implementation detail?
- Is the edge scenario real, or a token to pass the check?
- Is the root cause actually supported by the evidence?

## How Each Artifact Changes

| Artifact | Today | After |
|---|---|---|
| `/tmp` runtime (ledger, source-matrix, source-gap, query-plan, diagnosis, findings) | scaffold + hand-Write YAML/JSON | fully structured data; `merge`/`set`/derive; `render` previews |
| repo ADR | hand-written `.md` | data source of truth; `eg render` on demand |
| repo BDD | hand-written `.md` | data source of truth (scenario `#anchor` ids become data keys → `eg check` validates AT `derived_from` resolves) |
| repo CONTEXT | hand-written `.md` | data source of truth |
| `.eg/handoff/*.yml` | emitted by script | unchanged (already derived) |

Invariants from `METHOD.md` are preserved: user chooses entry; only `eg-enforce` assigns enforcement level; approved ADR/BDD substance is read-only for agents; BDD derives only from intent ADR; one-step write confirmation; stricter BDD approval gate.

## Build Plan — Vertical Slice

Prove the pattern on one low-blast-radius stage, then roll it out unchanged.

1. **Foundation + `eg-diagnose`.** Build the schema registry + CLI core (`new`/`merge`/`set`/`check`/`render`) + hard gate. Convert `eg-diagnose` end-to-end.
   - *Why diagnose first:* `/tmp`-only (no repo-doc flip yet), the four most structural artifacts (best test of `merge` + `check`), the concrete site of the `TBD` bug, and stage 0/optional so breakage is cheap.
   - *Verify:* run a real diagnosis through the CLI; confirm context drop vs. hand-Write, and that an unfilled field cannot reach completion.
2. **`eg-precipitate`.** Apply the same pattern; introduces repo ADR/CONTEXT data-flip.
3. **`eg-tdd`.** Introduces BDD data-flip + handoff; fold in the existing strong validators (`freeze-enforce-plan.py`, `validate-governance.py`).
4. **`eg-enforce`.** Mostly already scripted; pull under the CLI.

After each stage: rewrite its `SKILL.md` workflow to CLI verbs and delete the now-internal format docs.

## Status — built (2026-06-29)

All four stages run on the `eg` CLI (`skills/eg/cli/`). Verbs: `new`, `adr-new`,
`bdd-new`, `merge`, `set`, `check`, `seal`, `render`, `render-all`, `schema`,
plus `freeze`/`govern`/`commit-check` (tdd) and `pr-context`/`select`/`enforce`/
`notify`/`fix-handoff` (enforce). Stage-aware via `run.json`. CLI output passes
the original `validate-diagnosis`/`validate-precipitation`/`validate-governance`,
and `eg enforce` runs the real `enforce.py`.

**Data-in-repo flip is DONE** (decisions 4/5 realized). The committed source of
truth is the **data** `.yml`: `docs/adr/NNNN-slug.yml`, `docs/bdd/NNNN-slug.yml`,
`CONTEXT.yml`. The `.md` is **rendered and git-ignored** (`.gitignore` carries
`docs/adr/*.md`, `docs/bdd/*.md`, `/CONTEXT.md`). The legacy `.md` readers
(`validate-governance`, `validate-commit-scope`, `enforce.py`) are **not
migrated** — the tdd/enforce wrappers run `mirror.render_all` (data → `.md`)
before invoking them. `commit-scope` runs git in the real repo, which is why the
rendered `.md` must live in-place rather than a `/tmp` mirror. Wrappers reuse the
existing scripts; only `mirror.py` is new for this flip.

## Remaining

- **`eg` entrypoint.** Still invoked as `python3 $(readlink -f .agents/skills/eg)/cli/eg.py`; a `-m eg` / PATH shim is optional polish.
- **Delete superseded `*/scripts/new-*.py`, `render-*.py`** once confident (validators are still reused; scaffolders are not).
- **Migration of pre-flip committed `.md`** (if any real repo has them): a one-shot `.md` → `.yml` importer is not built; greenfield repos need none.
