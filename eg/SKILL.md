---
name: eg
description: User-invoked router for Executable Governance. Use only when the user explicitly invokes EG/$eg or asks to route an EG workflow; choose eg-precipitate, eg-tdd, or eg-enforce from repo evidence and ask one clarifying question when evidence is missing or conflicting.
---

# eg

Route Executable Governance. Do not implement, write artifacts, run tests, or judge gates.

Load references only as needed:

- `references/METHOD.md` for shared EG invariants.
- `references/ARTIFACT-MODEL.md` for repo and `/tmp/eg` artifact contracts.
- `references/STAGE-HANDOFF.md` for cross-stage handoff and fix-agent rules.

## Router Rule

The user decides whether to enter EG by invoking this skill. After entry, route by evidence.

Default to current repo. Search monorepo-wide only when the user explicitly says cross-repo, multi-repo, or names multiple repos.

Routing order:

1. PR/diff/merge/gate/review evidence -> `eg-enforce`.
2. Intent ADR exists and BDD is missing, draft, or review -> `eg-tdd` BDD approval gate.
3. Intent ADR and approved BDD exist, and implementation is requested -> `eg-tdd` implementation gate.
4. No intent ADR and user has feature/change intent -> `eg-precipitate` fast-intent.
5. Ambiguous terms, scope, constraints, or design decisions -> `eg-precipitate` grill.
6. Insufficient or conflicting evidence -> ask one clarifying question.

## Output

```md
EG route:
- Stage: eg-precipitate | eg-tdd | eg-enforce | blocked
- Evidence: ...
- Missing input: ...
- Next skill: ...
- Stop condition: ...
```

If blocked:

```md
EG route blocked:
- Candidate stages: ...
- Known evidence: ...
- Missing decision: ...
Recommended answer: ...
Hard question: ...
```

Ask only one question.

## Boundaries

- Do not infer BDD from a decision ADR.
- Do not route to tests when BDD is not approved.
- Do not write files.
- Do not run enforcement.
- Do not continue when route evidence conflicts.
