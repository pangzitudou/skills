# Interaction Protocol

Use this when asking questions, reducing cognitive load, or handling dense project-local language.

## Prime Directive

Reduce cognitive load, not decision pressure.

Questions must be easy to parse and hard to dodge.

## Per-Turn Shape

Prefer this shape:

```md
Current decision: {plain-language decision}
Recommended answer: {your recommendation and why}
Hard question: {one question}
```

If a write may be needed, add:

```md
Potential write: {artifact or "none yet"}
```

## One Decision at a Time

Ask one question per turn.

Do not combine:

- terminology clarification
- scope boundary
- architecture decision
- NFR checkpoint
- implementation sequencing

Pick the blocker that must be resolved next.

## Plain Language First

Start with what the user is deciding in plain language.

Bad:

```md
Given INV-015/016 and applies_to/best_mode coupling, reopen b' scope gate?
```

Good:

```md
Current decision: are we changing the coverage rule, or only fixing content that now fails it?
Recommended answer: fix the content. The rule is already catching fake coverage.
Hard question: what remaining failure proves the rule is wrong rather than the content?
```

## Local Terminology

Project-local terms and compressed symbols need expansion when first used or when confusion appears.

Examples:

- `INV-015/016`: name what invariant they protect.
- `b'`: say what design promise it refers to.
- `best_mode`: say what role it plays in validation.
- `coverage gate`: say what false claim it blocks.

Do not explain stable EG terms every time. Explain only when compression creates ambiguity.

## Local Symbol Table

For dense sessions, maintain a short in-session symbol table:

```md
Session symbols:
- INV-015/016: {plain meaning}
- b': {plain meaning}
- coverage gate: {plain meaning}
```

This table is not automatically written. Decide later whether each item belongs in `CONTEXT.md`, an ADR, or nowhere.

## Pressure Rules

Do:

- recommend an answer
- force trade-offs into the open
- ask for a choice when options conflict
- challenge contradictions against code, glossary, or ADRs

Do not:

- soften the decision into "either is fine"
- hide cost or reversibility
- keep explaining after enough context exists to choose

## Codebase and Artifact Checks

If existing code, `CONTEXT.md`, or ADRs can answer the question, inspect them before asking.

Call out contradictions directly:

```md
Current glossary says X. Your current wording implies Y. Which one governs?
```
