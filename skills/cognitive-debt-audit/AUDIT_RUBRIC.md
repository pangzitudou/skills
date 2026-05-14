# Audit Rubric

Use this rubric to identify cognitive debt in exported AI conversations. Focus on repeated or high-impact patterns, not every minor shortcut.

## 1. Skipped Modeling

The user asks for answers, summaries, or structures before stating their own understanding.

Signals:

- "直接告诉我答案"
- "帮我整理一下"
- No prior hypothesis, categorization, diagram, or attempted explanation.

Underlying debt:

- Problem decomposition
- Concept modeling
- Active generation of understanding

Payback actions:

- Write a 150-word personal explanation without looking at the AI answer.
- List 3 key concepts and their relationships.
- Draw or outline the topic structure from memory.

## 2. Skipped Retrieval Or Reading

The user lets AI replace contact with source material.

Signals:

- AI summarizes an article, paper, transcript, doc, or codebase, but the user never asks for source evidence.
- The user does not return to the original material to verify key claims.

Underlying debt:

- Source reading
- Evidence location
- Information-quality judgment

Payback actions:

- Find 3 original passages that support the AI summary.
- Compare one AI claim against the source.
- Mark one place where the AI may have over-interpreted.

## 3. Skipped Judgment

The user accepts AI conclusions without testing alternatives or boundaries.

Signals:

- No comparison between options.
- No "when would this fail?"
- No request for counterarguments, assumptions, risks, or trade-offs.

Underlying debt:

- Critical judgment
- Boundary awareness
- Trade-off reasoning

Payback actions:

- Write 3 reasons for accepting the conclusion.
- List 2 counterexamples or failure modes.
- State the conditions under which the answer would no longer apply.

## 4. Skipped Reconstruction

The user receives a process or solution but does not independently reproduce it.

Signals:

- AI gives steps, code, plan, proof, or workflow, and the user moves on immediately.
- No paraphrase, dry run, or second example.

Underlying debt:

- Independent execution
- Procedural memory
- Debugging and validation

Payback actions:

- Reproduce the process with the conversation closed.
- Rewrite the steps as a personal checklist.
- Apply the method to one nearby example.

## 5. Skipped Consolidation

The user gets a useful answer but leaves no durable artifact.

Signals:

- No principle, note, checklist, concept card, decision record, or next practice item.
- The same kind of question appears repeatedly across conversations.

Underlying debt:

- Long-term memory
- Knowledge structure
- Transfer across contexts

Payback actions:

- Extract 1 principle, 1 concept card, and 1 reusable prompt.
- Link the result to an existing note.
- Create a small "next time I will try first" rule.

## Severity Guide

- **Low**: The shortcut saved time and did not weaken future ability.
- **Medium**: The user got the task done but likely could not explain or repeat it.
- **High**: The user made or accepted an important decision without understanding, evidence, or judgment.

Prefer medium and high findings. Ignore low findings unless they repeat often.
