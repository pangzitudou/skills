# CONTEXT.md Format

## Structure

```md
# {Context Name}

{One or two sentence description of what this context is and why it exists.}

## Language

**Order**:
{A one or two sentence definition of the term.}
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Be opinionated.** When multiple words exist for the same concept, pick the best one and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences max. Define what it IS, not what it does.
- **Only include terms specific to this project's context.** General programming concepts (timeouts, error types, utility patterns) don't belong even if the project uses them extensively. Before adding a term, ask: is this a concept unique to this context, or a general programming concept? Only the former belongs.
- **Group terms under subheadings** when natural clusters emerge. If all terms belong to a single cohesive area, a flat list is fine.

## What CONTEXT.md is NOT

This is critical and frequently violated:

- **Not a spec.** No requirements, no scope, no acceptance criteria — those live in ADR (`type: intent`).
- **Not a scratchpad.** No open questions, no TBD, no notes-to-self.
- **Not a repository for decisions or constraints.** Those live in ADR (`type: decision` / `type: constraint`).

`CONTEXT.md` is a glossary and nothing else. If a resolved item has scope or decision content, it goes to an ADR; only its *terminology* belongs here.

## Single vs multi-context repos

**Single context (most repos):** One `CONTEXT.md` at the repo root.

**Multiple contexts:** A `CONTEXT-MAP.md` at the repo root lists the contexts, where they live, and how they relate:

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced` events; Billing consumes them to generate invoices
```

The skill infers which structure applies:

- If `CONTEXT-MAP.md` exists, read it to find contexts.
- If only a root `CONTEXT.md` exists, single context.
- If neither exists, create a root `CONTEXT.md` lazily when the first term is resolved.

When multiple contexts exist, infer which one the current topic relates to. If unclear, ask.

## Worked example

A tutoring-product `CONTEXT.md` after one grill session resolved a few terms:

```md
# AI Tutor

A personalized learning companion that guides a learner through structured content via conversation, tracking progress and adapting to weak points.

## Language

**Learner**:
A person who studies content through the tutor.
_Avoid_: student, user (too generic)

**Course**:
An ordered sequence of Lessons on a topic.
_Avoid_: track, path

**Lesson**:
The smallest unit of completable content; unlocks the next Lesson when done.
_Avoid_: module (reserved for code modules), section

**Weak Point**:
A topic or skill a learner has repeatedly failed to demonstrate, used to drive recommendations.
_Avoid_: gap, deficiency

**Tutor Session**:
One conversational exchange between a Learner and the tutor, scoped to a Lesson.
_Avoid_: chat, conversation (too generic)
```

Note what is **not** here: no scope (that's an ADR `type: intent`), no "use GPT-4" (that's an ADR `type: decision`), no "PII must be redacted" (that's an ADR `type: constraint`). Pure terminology.
