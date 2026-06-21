# Precipitation Triggers

Use this when deciding whether a conclusion is stable enough to write.

## Artifact Types

- `CONTEXT.md`: project language only.
- ADR `type: intent`: business scope and boundaries.
- ADR `type: decision`: hard-to-reverse choices with real trade-offs.
- ADR `type: constraint`: confirmed non-functional requirements.

BDD is never written here. BDD is a later derivation from approved intent ADRs.

## Domain Awareness

Before writing, inspect existing governance artifacts:

```text
/
├── CONTEXT.md
├── CONTEXT-MAP.md
└── docs/
    └── adr/
        ├── 0001-*.md
        └── 0002-*.md
```

If `CONTEXT-MAP.md` exists, use it to choose the right bounded context. Otherwise, use root `CONTEXT.md`.

Create files lazily. If no `CONTEXT.md` exists, create it only when the first term is confirmed. If no `docs/adr/` exists, create it only when the first ADR is confirmed.

## CONTEXT.md Trigger

Write when a term is resolved, disambiguated, canonicalized, or coined.

Do not write:

- implementation choices
- scope
- constraints
- open questions
- general programming terms

If a project-local symbol is temporary, keep it in the session summary instead of `CONTEXT.md`.

## Intent ADR Trigger

Write an intent ADR when the business scope is confirmed.

The scope triple must exist:

- In Scope
- Out of Scope
- Non Goals

Before closing, apply the four-question scope check:

| # | Question | Fail signal |
|---|---|---|
| 1 | Are In/Out/Non Goals all present? | Missing Non Goals |
| 2 | Is In Scope a boundary, not a sales pitch? | Adjectives do the work |
| 3 | Does Out of Scope pin high-drift neighbours? | Only obvious exclusions |
| 4 | Are Out of Scope and Non Goals separated? | Permanent rejection mixed with deferral |

If any check fails, do not close the ADR.

## Decision ADR Trigger

Default: do not write a decision ADR.

Write only when all three gates pass:

1. Hard to reverse: changing later costs meaningfully.
2. Surprising without context: future readers will ask why.
3. Real trade-off: genuine alternatives existed.

If any gate fails, skip the ADR. Noisy ADR logs erode trust.

## Constraint ADR Trigger

Write when a non-functional requirement is explicitly confirmed by the user.

Constraints often come from:

- the NFR checkpoint before closing an intent ADR
- explicit user concern about security, cost, performance, observability, policy, or structural requirements

Each constraint ADR must include a `domain`.

## Write Preview Requirement

Before writing any artifact, show:

- target artifact
- exact summarized content
- why the conclusion is stable enough

Wait for confirmation.
