---
name: eg
description: User-invoked router for Executable Governance.
disable-model-invocation: true
---

# eg

Route Executable Governance. While routing, do not implement, write artifacts, run tests, or judge gates.

Load references only as needed:

- `references/METHOD.md` for shared EG invariants.
- `references/ARTIFACT-MODEL.md` for repo and `/tmp/eg` artifact contracts.
- `references/STAGE-HANDOFF.md` for cross-stage handoff and fix-agent rules.

## Router Rule

The user decides whether to enter EG by invoking this skill. After entry, route by evidence.

Default to current repo. Search monorepo-wide only when the user explicitly says cross-repo, multi-repo, or names multiple repos.

Successful route completion criterion: the route is not done until the selected child skill has been loaded and started in the same turn. The next content after the route block must be that child skill's first required action, output, or question. Never tell the user to send another `$eg-*` command after a successful route.

Routing order:

1. PR/diff/merge/gate/review evidence -> `eg-enforce`.
2. Root-cause analysis, bug symptoms, evidence request, multiple symptoms, comparative module diagnosis, DB/log/API/runtime sources -> `eg-diagnose`.
3. Intent ADR exists and BDD is missing, draft, or review -> `eg-tdd` BDD approval gate.
4. Intent ADR and approved BDD exist, and implementation is requested -> `eg-tdd` implementation gate.
5. Root cause is known and user wants intent/scope/decision/ADR/acceptance alignment -> `eg-precipitate`.
6. No intent ADR and user has feature/change intent -> `eg-precipitate` fast-intent.
7. Ambiguous terms, scope, constraints, or design decisions -> `eg-precipitate` grill.
8. Insufficient or conflicting evidence -> ask one clarifying question.

Continuation:

- If route evidence is sufficient, print the route summary, read the selected child skill, and continue.
- If input is missing for routing, turn the most important gap into one answerable question and stop.
- If input is only missing for the next stage, route anyway and let the child skill collect it.

Child skill paths:

- `eg-diagnose`: `../eg-diagnose/SKILL.md`
- `eg-precipitate`: `../eg-precipitate/SKILL.md`
- `eg-tdd`: `../eg-tdd/SKILL.md`
- `eg-enforce`: `../eg-enforce/SKILL.md`

## Output

```md
EG route:
- Stage: eg-diagnose | eg-precipitate | eg-tdd | eg-enforce | blocked
- Evidence: ...
- Missing input: ...
- Next skill: ...
- Agent action: Loading and using <next skill> now.
- User question: none | <one routing question>
- Stop condition: ...
```

If `User question` is `none`, immediately continue into the selected child skill. Do not stop at the route block.

If blocked:

```md
EG route blocked:
- Candidate stages: ...
- Known evidence: ...
- Missing decision: ...
- Agent action: stop; do not load a child skill.
- User question: ...
Recommended answer: ...
Hard question: ...
```

Ask only one question. Do not merely describe missing input; ask for the decision needed to proceed.

## Boundaries

- Do not infer BDD from a decision ADR.
- Do not route to tests when BDD is not approved.
- During routing, do not write files or run enforcement.
- After routing, follow the selected child skill's boundaries.
- Do not continue when route evidence conflicts.
