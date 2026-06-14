# Polymorphic ADR Format

ADRs live in `docs/adr/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily — only when the first ADR is needed.

One file format. Three `type` values. Each type has its own precipitation trigger and its own enforcement form. The `type` field decides which governance logic applies — do not mix logic within a single ADR.

## Template (minimal skeleton)

```md
---
id: ADR-0001
type: intent | decision | constraint
status: draft | review | approved | deprecated
domain: (constraint only) performance | security | observability | cost
---

# {Short title}

## Context
{What this is about, and why it came up.}

## Decision
{For intent: the agreed scope. For decision: the chosen option. For constraint: the requirement.}

## (intent only)
## In Scope
- {confirmed capability}

## Out of Scope
- {not this time, maybe later}

## Non Goals
- {explicitly rejected, don't even propose}

## (intent, optional)
## Acceptance Criteria Seed
- {observable outcomes that will later derive BDD scenarios}

## Consequences
{Downstream effects, rejected alternatives. Optional for most.}
```

## The three types

### `type: intent` — business intent + scope

Carries what was originally a PRD: why, for whom, what's in, what's out, what's a non-goal.

- **Precipitation trigger**: business scope is confirmed — the In/Out/Non Goals triple takes shape.
- **Enforcement form**: Scope Gate (blocks intent drift).
- **Required field**: the three-piece Scope set (In Scope / Out of Scope / Non Goals).
- **Optional field**: Acceptance Criteria Seed (feeds BDD derivation later).
- **Review ruler** (must pass before closing): see the four questions below.

`In Scope` is a **confirmed boundary**, not a sales pitch. Test: does it still hold with adjectives stripped?

`Out of Scope` vs `Non Goals` must be distinguished:
- Out of Scope = "not this iteration, maybe later." Agent may note as a future suggestion; the capability's existence is legitimate.
- Non Goals = "never; don't even propose." A product-direction decision, not a scope decision.

Test: "might do it later" → Out of Scope; "doing it would violate the product's identity" → Non Goals.

### `type: decision` — architectural decision

Carries what was originally an ADR: why this design, why not the alternatives.

- **Precipitation trigger**: the three-gate test, **all three must pass**:
  1. Hard to reverse — changing your mind later costs meaningfully.
  2. Surprising without context — a future reader will wonder "why this way?"
  3. Real trade-off — genuine alternatives existed and one was picked for specific reasons.

  If any gate fails, skip the ADR. Do not precipitate reversible or obvious choices — a noisy decision log erodes trust in all of it.
- **Enforcement form**: can be translated to an Architecture Check.
- **Template weight**: minimal. "1–3 sentences: context, decision, why." An ADR can be a single paragraph. The value is recording *that* a decision was made and *why* — not filling out sections.

What qualifies: architectural shape (monorepo, event-sourced write model), integration patterns between contexts, technology choices with lock-in, boundary/scope decisions (including explicit no-s), deliberate deviations from the obvious path, constraints invisible in code, rejected alternatives worth remembering.

### `type: constraint` — non-functional requirement

Carries NFRs: performance, security, observability, cost, etc. One `type`, many `domain` values — do **not** open a separate type per domain. If a domain's constraints grow dense enough to blur, *then* consider splitting by enforcement form (quantifiable / policy / structural), never by domain label.

- **Precipitation trigger**: surfaced by NFR prompting at intent-ADR close, or raised explicitly by the user.
- **Enforcement form**: varies by constraint — quantifiable (CI threshold), policy (partial-automate + human review), structural (instrumentation must exist).
- **Required field**: `domain`.

## Numbering

Scan `docs/adr/` for the highest existing number and increment by one. Numbering is global across all types — ADR-0001 may be intent, ADR-0002 decision, ADR-0003 constraint.

## Status lifecycle

`draft → review → approved → deprecated` (or `superseded by ADR-NNNN`).

- Agent may freely edit `draft`.
- Agent may propose changes to `review`/`approved` but cannot unilaterally modify an approved ADR's substance.
- This protects against the agent rewriting the rules to pass its own implementation — the core safety boundary of Executable Governance.

## The four-question Scope ruler (intent-type, before closing)

| # | Question | Fail signal |
|---|---|---|
| ① | Are In/Out/Non Goals all present? | Missing Non Goals — only "do" and "don't" |
| ② | Is In Scope a boundary, not a sales pitch? | Adjectives; survives stripping |
| ③ | Does Out of Scope pin the highest-drift neighbours? | Only lists the obvious-not-done |
| ④ | Are Out of Scope and Non Goals distinguished? | Permanently-rejected items mixed into this-iteration-not-done |

Any one failing → send back, do not close.

## Worked examples

Three ADRs from the same tutoring product, one per type. Note how each stays in its lane — intent doesn't dictate tech, decision doesn't reopen scope, constraint doesn't re-derive behavior.

### Example A — `type: intent`

```md
---
id: ADR-0001
type: intent
status: review
---

# Learner Progress & Unlock

## Context
Learners need to move through a Course sequentially, with completion gating the next step. Without this, learners skip ahead and lose foundational context.

## Decision
Track per-Lesson completion and unlock the next Lesson in Course order.

## In Scope
- Record per-Lesson completion state (done / not done)
- Unlock the next Lesson in Course-defined order

## Out of Scope (not this iteration, maybe later)
- Cross-device progress sync
- Learning-data analytics and dashboards
- Re-locking an already-unlocked Lesson

## Non Goals (rejected; don't propose)
- Points / XP / leaderboards (no gamification)
- Forced sequential learning (learners may freely revisit unlocked content)

## Acceptance Criteria Seed
- Completing a Lesson makes the next Lesson viewable
- An uncompleted Lesson's successor stays locked
- Learners can revisit any already-unlocked Lesson

## Consequences
Drives a need for per-learner progress persistence (→ a future decision-type ADR).
```

This passed all four Scope questions before close. The Non Goals are product-direction decisions (gamification violates product identity), not scope deferrals.

### Example B — `type: decision`

```md
---
id: ADR-0002
type: decision
status: approved
---

# LLM Provider: Direct API over Aggregator

## Context
We need an LLM for Tutor Sessions. Options: call provider APIs directly, or use an aggregator (OpenRouter / LiteLLM).

## Decision
Call provider APIs directly. Re-evaluate if we exceed 2 providers or hit rate-limit pain.

## Consequences
- Chosen for: lower latency, full feature access, no intermediary failure mode.
- Rejected: aggregator's single-integration convenience — not worth the lock-in and extra hop yet.
- Cost: must implement per-provider adapters ourselves.
```

This passed the three-gate test: hard to reverse (adapters are real work), surprising without context ("why not just use the aggregator?"), real trade-off (convenience vs control). One paragraph — that's enough.

### Example C — `type: constraint`

```md
---
id: ADR-0003
type: constraint
status: approved
domain: security
---

# Redact Learner PII in Tutor Session Logs

## Context
Tutor Session logs are stored for debugging and observability. Learners may type personal data (names, emails) into the conversation.

## Decision
All Tutor Session logs must redact PII before persistence. Redaction runs before the log write, not after.

## Consequences
- Enforcement form: policy — partially automatable (pattern matching) but flagged for human review on ambiguous cases.
- Feeds an architecture check: a log-write path that bypasses redaction is a violation.
```

This was surfaced by NFR prompting at the close of ADR-0001 ("does learner progress touch security?"). The `domain: security` tag and the stated enforcement form (policy + architecture check) make it ready for eg-enforce to consume later.
