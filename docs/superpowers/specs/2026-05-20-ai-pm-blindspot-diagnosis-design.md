# AI PM Blindspot Diagnosis Skill Design

## Goal

Create an `ai-pm-blindspot-diagnosis` skill that helps early AI product managers turn unknown unknowns into known unknowns.

The skill is a diagnostic interview, not a lesson. It exposes blind spots through a fixed AI product case, scenario questions, evidence-based scoring, and a final report.

## Target User

- Primary user: product managers with 0-2 years of AI PM experience, especially people moving from non-AI PM work into AI products.
- The skill may be useful for adjacent users, but the first version optimizes for this audience.

## Fixed Case

- Product: K12 math AI tutor.
- Product stage: before PRD or solution review.
- Primary user: student.
- Paying or supervising user: parent.
- Out of scope for the case: school procurement, teacher workbench, classroom management.
- Core success metric: improvement in student mastery of target knowledge points.

## Scope

The skill does:

- Ask a fixed diagnostic sequence across 16 AI PM decision modules.
- Accept "I don't know" as valid input and record it as a blind spot.
- Ask at most one follow-up when an answer is vague or incomplete.
- Withhold teaching, correct answers, rubrics, and resources during diagnosis.
- Produce a final Markdown diagnostic report.

The skill does not:

- Teach AI PM.
- Generate a learning plan.
- Review or rewrite a PRD.
- Design the AI tutor product for the user.
- Save the user's diagnostic report by default.
- Provide external resource links in the final report.

## Module Map

All 16 modules are asked. Users cannot skip modules.

1. Business problem definition
2. AI necessity
3. User workflow
4. Model capability boundaries
5. Prompt and instruction design
6. Personalized learning path
7. Agent and tool use
8. Data quality and data permissions
9. Learning outcome evaluation and evals
10. Logs and feedback loops
11. Hallucination and wrong explanations
12. Safety and prompt injection
13. Privacy and minor compliance
14. Cost, latency, and reliability
15. Rollout, monitoring, and rollback
16. Business metrics and ROI

## Interaction Flow

1. Open with rules:
   - This is diagnosis, not teaching.
   - The case is fixed: K12 math AI tutor before PRD or solution review.
   - All 16 modules will be asked.
   - Users cannot skip.
   - Users may answer "I don't know".
   - Each answer should be 3-8 sentences if possible.
   - Correct answers and scoring rubrics are withheld until the final report.
2. Show only the module names.
3. Ask one scenario question at a time.
4. Maintain an internal diagnostic ledger:
   - module
   - user evidence
   - missing variables
   - risk level
   - follow-up asked
   - final judgment
5. If the user says "I don't know", record a blind spot and move to the next module.
6. If the user gives a vague answer, ask one concrete follow-up.
7. If the user asks for the correct answer mid-diagnosis, refuse briefly and continue diagnosis.
8. After all modules, output the final report.

## Scoring

Use four levels:

- No obvious blind spot: answer covers key risks, tradeoffs, and validation methods.
- Shallow recognition: answer recognizes terms but lacks decision standards or validation.
- Clear blind spot: answer misses key variables that would damage product quality.
- High-risk misjudgment: answer would likely cause PRD failure, unsafe launch, cost blowup, compliance exposure, or false product validation.

Do not produce a numeric score.

## Report Shape

The final report contains:

- Hard conclusion: whether the user should enter PRD or solution review.
- Diagnostic confidence:
  - High: enough concrete evidence across most modules.
  - Medium: mixed concrete and vague answers.
  - Coarse: many "I don't know" answers or too little evidence for fine-grained differentiation.
- Top 3 highest-risk blind spots, each with:
  - module
  - conclusion
  - user evidence
  - missing variables
  - risk
  - smallest next action
- Remaining 13 modules in a compact table.
- Repeated cognitive patterns.
- Minimal remediation actions without external links.

## File Structure

```text
ai-pm-blindspot-diagnosis/
  SKILL.md
  references/
    module-map.md
    question-bank.md
    scoring-rubric.md
    report-template.md
```

## Acceptance Criteria

- `SKILL.md` stays concise and delegates heavy content to references.
- The question bank contains exactly 16 modules.
- Each module has one main scenario question and one follow-up.
- The scoring rubric includes "I don't know", vague answer, no-skip, and hard-conclusion rules.
- The report template includes hard conclusion, confidence, Top 3 blind spots, remaining modules, cognitive patterns, and minimal remediation.
- No implementation requires network access or external services.
