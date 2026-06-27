# EG Method

Executable Governance makes intent visible enough to constrain agents.

## Stages

0. `eg-diagnose` (optional): analyze bugs/problems into evidence-backed root causes and fix options. Writes only `/tmp/eg/<run-id>` diagnosis artifacts.
1. `eg-precipitate`: align language, scope, decisions, constraints. Writes CONTEXT and ADR only after stable confirmation.
2. `eg-tdd`: derive approved BDD from intent, then tests and implementation. Emits `/tmp/eg/<run-id>/ledger.json`, repo `.eg/handoff/<run-id>.yml`, and an implementation commit.
3. `eg-enforce`: PR-time gate. Reads diff, CI facts, repo handoffs, and artifacts. Reports findings and asks one next question.

## Invariants

- User chooses whether to enter EG.
- Router chooses stage from evidence.
- Diagnosis is optional and may not edit code, data, repo artifacts, or commits.
- BDD must derive from an intent ADR.
- Decision ADRs constrain implementation and tests, but never seed BDD.
- Artifact status crosses stages; enforcement level does not.
- Only `eg-enforce` assigns enforcement level, next step, waiver consumption, and gate.
- Approved ADR/BDD substance is read-only for agents. Agents may propose changes, not edit to make code pass.
- Repo artifacts are stable contracts. `/tmp/eg` artifacts are run state and debug/provenance.

## Confirmation

Artifact write confirmation is one-step:

1. Show preview.
2. User confirms.
3. Write immediately.

Ask again only when the preview became inaccurate, the path conflicts, multiple artifacts were not all confirmed, or approved artifact substance would change.

BDD approval is stricter:

- Draft BDD may be written directly.
- Approved BDD requires human preview and explicit approval.
- On approval, the agent sets `status: approved`, writes approval metadata, freezes the enforce plan and CI facts contract, then follows the user's stop/continue preference. Stopping before the freeze is forbidden.

## Commits

`eg-tdd` and fix agents auto-commit only verified, in-scope changes. They never commit `/tmp/eg` or unrelated dirty files.

If fix requires changing approved ADR/BDD substance, stop and ask the human.
