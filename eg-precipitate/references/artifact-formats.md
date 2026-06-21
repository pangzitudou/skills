# Artifact Formats

Use this only after the user confirms a write preview.

## CONTEXT.md

`CONTEXT.md` is a glossary and nothing else.

```md
# {Context Name}

{One or two sentence description of this context.}

## Language

**{Canonical Term}**:
{One or two sentence definition of what it is.}
_Avoid_: {rejected synonym}, {ambiguous synonym}
```

Rules:

- Define what the term is, not what it does.
- Prefer project-specific terms over general programming terms.
- Keep definitions to one or two sentences.
- List rejected synonyms under `_Avoid_` when useful.
- Do not include scope, requirements, decisions, constraints, open questions, or notes.

For multiple bounded contexts, use `CONTEXT-MAP.md` to choose the right `CONTEXT.md`.

## ADR Location and Numbering

ADRs live in `docs/adr/`.

Use sequential global numbering across all types:

```text
0001-slug.md
0002-slug.md
0003-slug.md
```

Scan existing ADR filenames, find the highest number, and increment by one.

## ADR Skeleton

```md
---
id: ADR-0001
type: intent | decision | constraint
status: draft | review | approved | deprecated
domain: security | cost | performance | observability
---

# {Short title}

## Context
{What this is about and why it came up.}

## Decision
{For intent: agreed scope. For decision: chosen option. For constraint: requirement.}

## Consequences
{Downstream effects or rejected alternatives. Optional when obvious.}
```

For `constraint`, include `domain`.

## Intent ADR Additions

Intent ADRs must include:

```md
## In Scope
- {confirmed capability}

## Out of Scope
- {not this iteration, maybe later}

## Non Goals
- {explicitly rejected; do not propose}
```

Optional:

```md
## Acceptance Criteria Seed
- {observable outcome for later BDD derivation}
```

`Acceptance Criteria Seed` is not BDD. Do not write scenarios here.

## Decision ADR Weight

Decision ADRs should usually be short:

- 1-3 sentences of context
- chosen option
- why alternatives were rejected

Do not pad ADRs to fill sections.

## Constraint ADR Requirements

Constraint ADRs must state:

- requirement
- domain
- enforcement shape when known: quantifiable, policy, or structural

Examples:

- security: policy, often partly automatable
- cost: quantifiable budget or threshold
- performance: latency or throughput threshold
- observability: required logs, traces, metrics, or instrumentation

## Status Rules

Lifecycle:

```text
draft -> review -> approved -> deprecated
```

Agent may freely edit `draft`.

Agent may propose changes to `review` or `approved`, but cannot unilaterally modify the substance of an approved ADR.
