# Failure Modes

Use this when the session feels noisy, circular, too abstract, or too eager to write.

## Bad Interaction

Do not:

- ask abstract questions without a concrete decision point
- explain the whole methodology when one decision is needed
- use project symbols without expansion on first use
- keep pushing after the user says they do not understand
- make questions easier to answer by hiding trade-offs
- ask multiple unrelated questions in one turn

Fix:

```md
Current decision: {plain-language decision}
Recommended answer: {your answer}
Hard question: {one question}
```

## Bad Terminology Handling

Do not:

- put every shorthand into `CONTEXT.md`
- leave stable project-local terms undefined
- confuse temporary session shorthand with durable domain language

Use three buckets:

- stable domain term -> `CONTEXT.md`
- stable governance or project symbol -> ADR text or ADR appendix
- temporary shorthand -> session symbol table only

## Bad Artifact Writing

Do not:

- write before confirmation
- write while still exploring
- use artifacts as scratchpads
- batch unresolved thoughts for later cleanup
- write decision ADRs for reversible or obvious choices
- put scope, decisions, or constraints into `CONTEXT.md`

## Bad Scope Handling

Do not close an intent ADR when:

- Non Goals are missing
- In Scope is a sales pitch
- high-drift neighbours are not excluded or deferred
- Out of Scope and Non Goals are mixed

## Bad Stage Boundary

Do not:

- write BDD during precipitation
- run tests
- enforce gates
- implement the feature
- rewrite approved ADR substance without human approval

Say when the next stage owns the work.
