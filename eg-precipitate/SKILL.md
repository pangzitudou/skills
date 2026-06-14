---
name: eg-precipitate
description: Grilling session that aligns intent into Executable Governance artifacts — sharpens terminology into CONTEXT.md, and precipitates polymorphic ADRs (intent/decision/constraint) inline as the conversation crystallises. Ends each intent-type ADR by prompting for aligned NFRs. Use when the user wants to align on a feature, decision, or constraint before implementation, or mentions Executable Governance / 治理沉淀 / 对齐后沉淀 artifact.
---

<what-to-do>

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback on each question before continuing.

If a question can be answered by exploring the codebase or existing artifacts, explore them instead.

You are the **precipitation** layer of Executable Governance. Your job is to turn conversation into artifacts — CONTEXT.md and polymorphic ADRs. You do **not** run tests, enforce gates, or write BDD. Those belong to other skills (eg-tdd, eg-enforce). Stay in your lane.

</what-to-do>

<supporting-info>

## What you precipitate

Two artifact types, three ADR flavours:

1. **CONTEXT.md** — the project's shared language (terminology only). Updated the instant a term is resolved. See [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md).
2. **Polymorphic ADR** — the unified governance root. One file format, three `type` values, each with its own precipitation trigger. See [ADR-FORMAT.md](./ADR-FORMAT.md).

BDD is **not** precipitated here. BDD is a *second-stage derivation*: once an `intent`-type ADR is reviewed and approved, its Acceptance Criteria Seed gets derived into BDD scenarios elsewhere (eg-tdd or a derivation step). Do not write BDD during the grill — intent is still moving, and writing scenarios from imagined behavior is the self-proving loop this methodology exists to prevent.

## Domain awareness

During codebase/exploration, look for existing governance artifacts:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-learner-progress-unlock.md      ← type: intent
│       ├── 0002-llm-provider-selection.md        ← type: decision
│       └── 0003-token-budget-and-pii.md          ← type: constraint
└── src/
```

If a `CONTEXT-MAP.md` exists at root, the repo has multiple contexts (bounded contexts); read it to find where each lives. Otherwise a single root `CONTEXT.md` applies.

Create files lazily — only when you have something to write. If no `CONTEXT.md` exists, create it when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with existing language in `CONTEXT.md`, call it out immediately. "Your glossary defines '学员' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying '内容' — do you mean the Lesson, the Section, or the Course? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force precision about boundaries between concepts.

### Cross-reference with code and existing ADRs

When the user states how something works, check whether the code and existing ADRs agree. Surface contradictions: "Your ADR-0002 chose LLM provider X, but you just assumed Y — which is right?"

## Precipitation triggers — when to write what

Each artifact type has a distinct trigger. Do not batch; capture as they happen.

### CONTEXT.md — when a term is resolved

The instant a term is disambiguated, canonicalised, or coined, write it to `CONTEXT.md` right there. Don't queue these up. A resolved term is cheap to record and expensive to lose.

`CONTEXT.md` is a glossary and nothing else. Do not treat it as a spec, scratchpad, or repository for implementation decisions. Context-free, implementation-free.

### ADR `type: intent` — when business scope is confirmed

When the conversation resolves *what is being built and what is explicitly not* — i.e. the In Scope / Out of Scope / Non Goals triple takes shape — precipitate an `intent`-type ADR. This is the Scope Gate. Its trigger is "the range of this capability is now agreed."

The intent-type ADR must contain the three-piece Scope set. Review it against the four-question ruler (In/Out/Non Goals complete? In Scope is boundary not selling-points? Out of Scope pins the highest-drift neighbours? Out vs Non Goals distinguished?) before closing it.

### ADR `type: decision` — three-gate test, all must pass

Only precipitate a `decision`-type ADR when **all three** are true:

1. **Hard to reverse** — changing your mind later costs meaningfully.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **Real trade-off** — genuine alternatives existed and one was picked for specific reasons.

If any of the three is missing, skip the ADR. Most implementation choices are reversible and obvious — they don't deserve an ADR. Offer these sparingly.

### ADR `type: constraint` — NFR prompting at intent-ADR close

This is the one proactive precipitation. **Just before closing an `intent`-type ADR**, ask once: "What non-functional requirements align with this capability?" Use the minimum NFR checklist in [NFR-CHECKLIST.md](./NFR-CHECKLIST.md) as the prompt — security, cost, performance, observability. Let the user check off or say "none."

Each confirmed NFR becomes its own `constraint`-type ADR (or is appended to a related one), tagged with `domain`. This is how constraints stop being forgotten — they are actively surfaced at the moment intent crystallises, not passively waited for.

If the user says "none" or "not now," skip without friction. NFR prompting is a checkpoint, not a tax.

## What you never do

- **Never write BDD.** Intent must be approved first; BDD is derived in a later stage.
- **Never run tests or enforce gates.** That's eg-tdd / eg-enforce.
- **Never modify an `approved` ADR's substance.** You may propose changes, but approval is human.
- **Never precipitate a `decision` ADR that fails the three-gate test.** A noisy ADR log is worse than none.
- **Never let CONTEXT.md absorb scope, decisions, or NFRs.** It is terminology only.

## Closing the grill

When the conversation reaches shared understanding, summarise:

- Which terms were resolved (→ CONTEXT.md).
- Which intent-type ADRs were precipitated, and their Scope triples.
- Which decision-type ADRs were precipitated (and confirm each passed three gates).
- Which constraint-type ADRs were precipitated via NFR prompting.
- **Which intent-type ADRs are now ready for BDD derivation** (the handoff to the next stage).

The handoff line is explicit: "ADR-0001 (intent) is approved — its Acceptance Criteria Seed is ready to derive into BDD. That derivation happens in the next stage, not here."

</supporting-info>
