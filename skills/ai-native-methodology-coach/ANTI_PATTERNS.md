# Anti-Patterns

Use this when the user seems to be bringing old work habits into AI-native work.

## Premature Technology Control

Smell:

- "Use Vue/React/FastAPI because I like it."
- "Do not use this stack because I dislike it."
- "Follow the old architecture unless impossible."

Coach response:

- Ask whether the stack is a real constraint.
- Move the user back to target effect, boundaries, acceptance, maintenance ability, migration cost, and compatibility.
- Suggest asking an execution thread to compare options after requirements are clear.

## Existing-Implementation Bias

Smell:

- "Just modify it in the current structure."
- "Refactor, but do not change the design."
- "Keep the current model because that is how the project works now."

Coach response:

- Ask what the ideal design would be if starting from the current requirement.
- Treat the old structure as an input, not a law.
- If migration risk is real, guide the user to compare ideal design and incremental migration.

## Feature-First Instead of Requirement-First

Smell:

- "Build a dashboard."
- "Add an approval page."
- "Make a chatbot."

Coach response:

- Ask what business problem the feature solves.
- Ask who uses it and when.
- Ask how the user will know it worked.
- Do not enter Plan until target and acceptance are observable.

## Implementation Before SPEC

Smell:

- The user asks for code, task breakdown, or architecture while the goal is still vague.
- The user wants to "let AI try first" without a checkpoint.

Coach response:

- Send the user back to Brainstorm, Grill Me, or SPEC.
- Provide a prompt for clarifying the requirement.
- Explain that early implementation amplifies rework.

## Trust by Vibe

Smell:

- "AI said it is done, so it should be fine."
- "The code looks okay."
- "The demo ran once."

Coach response:

- Use staged checks: unit tests, smoke-level E2E, AI self-review, and human business acceptance.
- Ask the user what output they have and which stage it belongs to.
- Do not let implementation replace acceptance.

## Distrusting AI by Taking Back Control

Smell:

- The user responds to one AI mistake by specifying every implementation step.
- The user starts manually debugging everything instead of asking AI to inspect and repair.

Coach response:

- Acknowledge the risk.
- Move to checklists and smaller loops, not human micromanagement.
- Ask AI to self-review, propose tests, or compare with another AI.

## Addition Before Subtraction

Smell:

- Adding analytics, performance tuning, edge polish, workflows, permissions, dashboards, and reports before the core function is clear.
- Mixing "nice to have" with "must work".

Coach response:

- Separate core requirement from later additions.
- Ask what can be removed without hurting the first useful outcome.
- Push non-core work to later stages unless it is a real constraint.

## Generic AI Advice Drift

Smell:

- The user asks broad AI productivity questions that are not covered by the internal methodology.
- The assistant starts giving internet-style best practices.

Coach response:

- Say the current methodology does not cover the question.
- Suggest recording a methodology gap.
- Do not invent generic guidance.

