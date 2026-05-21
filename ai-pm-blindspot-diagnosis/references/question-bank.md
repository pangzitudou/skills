# AI PM Blindspot Question Bank

Ask in order. Each module has one main question and one follow-up. Do not show answer signals or omissions to the user.

## 1. Business Problem Definition

Main question: You are preparing a PRD for a K12 math AI tutor. What exact student problem does the first version solve, and what does it deliberately not solve?

Follow-up: If you had to reject three tempting features from v1, what would they be and why?

Excellent answer signals:
- Names grade range, math scope, student situation, current workaround, and measurable learning job.
- Defines exclusions such as open-ended homework help, full curriculum replacement, exam prediction, or teacher workflow.
- Connects scope to learning mastery, not generic engagement.

Dangerous omissions:
- Says "improve learning efficiency" without narrowing user, situation, or math scope.
- Treats every K12 student as one user type.
- Does not define what v1 will refuse or defer.

## 2. AI Necessity

Main question: In this tutor, which parts truly need AI, and which parts should use simpler non-AI logic?

Follow-up: What evidence would make you decide that AI is not worth using for one of those parts?

Excellent answer signals:
- Separates adaptive explanation, misconception diagnosis, and natural-language interaction from deterministic grading, progress tracking, scheduling, and content lookup.
- Compares AI to rules, search, static content, human tutor workflow, and solver tools.
- Names cost, risk, latency, and learning value as reasons to avoid AI in some paths.

Dangerous omissions:
- Assumes AI should power everything because product is an AI tutor.
- Cannot name a non-AI baseline.
- Has no kill condition for AI usage.

## 3. User Workflow

Main question: Describe the full student workflow from getting stuck on a math problem to later reviewing the same knowledge point.

Follow-up: At which moments should the AI stop helping, escalate, or switch mode?

Excellent answer signals:
- Covers input, problem understanding, hinting, step-by-step guidance, student attempt, feedback, misconception labeling, next practice, review, and parent visibility.
- Distinguishes student experience from parent supervision.
- Defines AI entry and exit points.

Dangerous omissions:
- Describes only a chat box.
- No loop from a single problem to later mastery.
- No handling for frustration, repeated failure, or over-reliance.

## 4. Model Capability Boundaries

Main question: In K12 math tutoring, what should the model not be trusted to do by itself?

Follow-up: How would you constrain or verify those risky outputs before a student sees them?

Excellent answer signals:
- Names arithmetic errors, invalid reasoning steps, grade-inappropriate explanations, overconfident uncertainty, hallucinated curriculum facts, and unsafe advice.
- Uses tools, structured solution checks, answer verification, confidence handling, fallback, and escalation.
- Treats model output as untrusted until verified for critical paths.

Dangerous omissions:
- Says the model is good enough if benchmark accuracy is high.
- Ignores reasoning-step correctness.
- No boundary between generated explanation and verified answer.

## 5. Prompt and Instruction Design

Main question: What instructions would you give the tutor so it helps the student think instead of immediately giving the answer?

Follow-up: How would you test whether the instruction still holds when the student asks for the direct answer?

Excellent answer signals:
- Includes Socratic hints, step gating, age-appropriate language, misconception probing, refusal to directly solve too early, and mode changes after student effort.
- Plans prompt tests with adversarial and normal student inputs.
- Does not rely on one generic role prompt.

Dangerous omissions:
- Only says "you are a patient math tutor".
- No distinction between hint, explanation, answer, and practice modes.
- No test for instruction following.

## 6. Personalized Learning Path

Main question: How would the product decide that a student has or has not mastered a target knowledge point?

Follow-up: If the student gets the final answer right but uses a wrong method, what should happen?

Excellent answer signals:
- Uses tagged knowledge points, correctness, reasoning process, attempt count, time, hint usage, error type, spaced review, and retention.
- Separates answer correctness from concept mastery.
- Handles cold start and updates mastery over time.

Dangerous omissions:
- Treats one correct answer as mastery.
- Personalization based only on chat history or self-report.
- No model for forgetting, review, or misconception persistence.

## 7. Agent and Tool Use

Main question: What external tools or structured systems should this tutor call, and when?

Follow-up: What should happen if a tool result conflicts with the model's explanation?

Excellent answer signals:
- Names equation solver, curriculum or knowledge-point map, question bank, user profile, progress system, content safety checks, and logging.
- Defines when tools are mandatory versus optional.
- Handles tool failure and conflict resolution.

Dangerous omissions:
- Lets the model generate all facts, questions, and checks unaided.
- No conflict policy.
- No tool permission or traceability model.

## 8. Data Quality and Data Permissions

Main question: What data does the tutor need to work well, and what data should it avoid collecting?

Follow-up: How would poor or missing student history change the product behavior?

Excellent answer signals:
- Needs grade, curriculum scope, problem attempts, error labels, hint usage, progress, and parent consent state.
- Avoids excessive personal data, unrelated school records, sensitive information, and indefinite raw conversation retention.
- Plans cold-start behavior and data quality checks.

Dangerous omissions:
- Says "collect as much data as possible".
- No distinction between product data, learning data, and sensitive personal data.
- No plan for stale, wrong, or missing history.

## 9. Learning Outcome Evaluation and Evals

Main question: Before launch, how would you prove the tutor improves learning rather than merely answers math questions correctly?

Follow-up: If a student question has no single standard answer, how would you evaluate the tutor response?

Excellent answer signals:
- Defines learning outcome metrics, pre/post checks, held-out problems, misconception repair, retention, expert review, rubric grading, and online experiment design.
- Separates answer accuracy, explanation quality, and student mastery.
- Includes failure case sets.

Dangerous omissions:
- Measures only model answer correctness.
- Uses only manual spot checks.
- No test set, rubric, baseline, or learning outcome.

## 10. Logs and Feedback Loops

Main question: After launch, what logs or feedback would reveal that students are not actually learning?

Follow-up: How would those signals turn into product or model improvements?

Excellent answer signals:
- Tracks attempts, hints, step errors, repeated failures, abandonment, corrections, parent reports, student confusion, model refusals, and outcome changes.
- Converts logs into labeled failure samples, eval updates, prompt changes, product fixes, or content improvements.
- Distinguishes complaint volume from learning signal.

Dangerous omissions:
- Tracks only DAU, retention, or user complaints.
- No failure taxonomy.
- No loop from logs to evals or product changes.

## 11. Hallucination and Wrong Explanations

Main question: What are the highest-risk ways this tutor could teach math incorrectly, and how would you catch them?

Follow-up: If a wrong explanation already reached students, what is the response process?

Excellent answer signals:
- Names wrong final answer, invalid step, plausible but false shortcut, grade-inappropriate method, and overconfident correction of a student.
- Uses verification, severity levels, audit sampling, user reporting, rollback, correction, and parent communication where needed.
- Treats wrong teaching as a learning-harm incident, not just a model bug.

Dangerous omissions:
- Assumes students or parents will report bad explanations.
- No severity model.
- No corrective action after exposure.

## 12. Safety and Prompt Injection

Main question: How could a student misuse or jailbreak this tutor, and what should the product do about it?

Follow-up: How would you test these attacks before launch?

Excellent answer signals:
- Covers direct answer extraction, prompt leakage, bypassing tutoring mode, inappropriate content, self-harm or abuse disclosures, cheating behavior, and tool abuse.
- Uses safety policies, input/output checks, tool isolation, instruction hierarchy, adversarial test sets, and audit logs.
- Recognizes that curious students are adversarial users in this context.

Dangerous omissions:
- Says "students are children, not attackers".
- Relies only on a stronger system prompt.
- No adversarial test plan.

## 13. Privacy and Minor Compliance

Main question: What privacy and compliance issues matter because this product involves K12 students?

Follow-up: How should parent access, deletion, and model training use be handled?

Excellent answer signals:
- Names parent consent, data minimization, retention, deletion, access controls, auditability, training-data restrictions, and legal review.
- Separates parent visibility from student privacy and safety.
- Avoids presenting legal certainty without review.

Dangerous omissions:
- Treats privacy as a checkbox in terms of service.
- No consent or deletion design.
- Assumes student conversations can be freely reused for training.

## 14. Cost, Latency, and Reliability

Main question: If 100,000 students use this tutor daily with multi-turn math conversations, how would you estimate and control cost, latency, and reliability?

Follow-up: Which user paths need the expensive model, and which can use cheaper paths?

Excellent answer signals:
- Estimates tokens, turns, tool calls, peak traffic, model routing, caching, batching, timeout, fallback, monitoring, and unit economics.
- Separates critical tutoring paths from low-risk cheap paths.
- Connects latency to student experience and learning flow.

Dangerous omissions:
- Says cost can be optimized later.
- No per-session or per-student unit model.
- No fallback for model or tool outages.

## 15. Rollout, Monitoring, and Rollback

Main question: How would you launch this tutor safely before exposing it to all students?

Follow-up: What specific signal would force rollback or kill-switch activation?

Excellent answer signals:
- Uses limited cohorts, age/grade constraints, expert review, parent controls, monitoring thresholds, incident severity, rollback, and kill switches.
- Defines red-line metrics for wrong explanations, unsafe responses, latency, and learning harm.
- Does not treat launch as one approval event.

Dangerous omissions:
- Launches after internal acceptance only.
- No rollback threshold.
- No owner for monitoring or incident response.

## 16. Business Metrics and ROI

Main question: How would you prove this AI tutor is worth building and charging for?

Follow-up: What would make the business case fail even if students like the chat experience?

Excellent answer signals:
- Connects mastery lift, parent willingness to pay, retention, conversion, support cost, model cost, gross margin, and alternatives.
- Distinguishes engagement from paid learning value.
- Names failure cases such as high usage with poor margin, novelty retention decay, or weak learning effect.

Dangerous omissions:
- Uses "AI is hot" or "students will like it" as business proof.
- No unit economics.
- No link between learning outcome and payment.
