# Anti-Patterns

Use this when the user seems to be bringing old work habits into the AI-assisted delivery workflow.

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

## Implementation Before Requirement Clarity

Smell:

- The user asks for code, task breakdown, or architecture while the goal is still vague.
- The user wants to "let AI try first" without a checkpoint.

Coach response:

- Send the user back to Brainstorm, Grill Me, Prototype, or SPEC review.
- Provide a prompt for clarifying the requirement.
- Explain that early implementation amplifies rework.

## SPEC-as-Manual Confusion

Smell:

- The user says "write SPEC" and AI starts writing README, API fields, database schema, test cases, or implementation paths.
- The user treats SPEC as a technical方案 or说明书 instead of a contract.
- The user wants to put startup commands, SQL, controller/service paths, deployment steps, or meeting notes into SPEC.
- The user wants to put one prototype's business details directly into a company-level common SPEC.

Coach response:

- Restate that SPEC is a contract: goal, roles, scope, flow, rules, boundaries, and acceptance.
- Move startup commands to README or DEVELOPMENT.
- Move API fields to API docs.
- Move database schema to DATA_MODEL or DATABASE.
- Move test details to TESTING and deployment steps to DEPLOYMENT.
- If it is a company-level common SPEC, separate reusable rules from project-specific details before writing anything.

## Over-Standardizing

Smell:

- Every small request creates a new company-level common SPEC.
- One-off client exceptions become global rules.
- Unvalidated prototype details become standards.

Coach response:

- Ask what repeated drift or inconsistency the standard prevents.
- Separate reusable rules from temporary choices.
- Prefer a project/feature SPEC for one business feature.
- Prefer updating an existing common standard over creating a new one.

## Trust by Vibe

Smell:

- "AI said it is done, so it should be fine."
- "The code looks okay."
- "The demo ran once."

Coach response:

- Use staged checks: unit tests, smoke-level E2E, AI self-review, and human business acceptance.
- Ask the user what output they have and which stage it belongs to.
- Do not let implementation replace acceptance.

## Random Human Clicking

Smell:

- The human opens the page, clicks a few things, and says it seems fine.
- There is no QA plan, no evidence, and no pass/fail criteria.
- Only the happy path was checked.

Coach response:

- Ask AI to generate a human QA checklist.
- Have the human execute as AI's hands and eyes.
- Require structured feedback before acceptance.

## Manual Debugging Takeover

Smell:

- After seeing a bug, the human starts reading code or guessing fixes.
- The human reports "it is broken" without steps, data, screenshots, or expected result.

Coach response:

- Move the user to the human feedback template.
- Ask for exact operation steps, actual result, expected result, evidence, reproducibility, and business impact.
- Feed the evidence back to AI for repair.

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

## Role-Silo Thinking

Smell:

- "I am backend, so I cannot judge the page."
- "This is frontend/UI/testing work, not my responsibility."
- "Let the designer/tester/product person decide before I use AI."

Coach response:

- Remind the user that the target is reviewable movement through the AI-assisted delivery workflow.
- Use AI to create the missing artifact: HTML prototype, QA checklist, SPEC, Plan, or acceptance checklist.
- Keep human business judgment, but do not hide behind old role boundaries.

## Text-Only Requirement Drift

Smell:

- The user keeps discussing a screen, process, or workflow only in text.
- Stakeholders disagree because everyone imagines a different interface or flow.
- The user wants to enter Plan without seeing the path.

Coach response:

- Recommend a quick HTML prototype as a requirement validation artifact.
- Make clear that this is not production implementation.
- Review the prototype before Plan.
