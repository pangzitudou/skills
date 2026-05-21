# Scoring Rubric

Score evidence, not confidence or fluency. A polished vague answer is still a weak answer.

## Risk Levels

### 未发现明显盲区

Use when the answer covers:

- Relevant decision variables.
- Product tradeoffs.
- Verification method.
- Failure mode or boundary.
- Case-specific implications for a K12 math AI tutor.

Do not use this level just because the answer sounds experienced.

### 浅层认知

Use when the answer:

- Names the right concept but lacks operating criteria.
- Says what should happen but not how to judge success.
- Gives process labels without thresholds, examples, or evidence.
- Uses generic AI PM language that could apply to any product.

### 明确盲区

Use when the answer:

- Misses a key variable for the module.
- Cannot explain how to verify the claim.
- Confuses related concepts.
- Treats a serious design decision as obvious.
- Says "不知道", "没想过", "不确定", or equivalent.

### 高风险误判

Use when the answer would likely cause:

- PRD or solution review failure.
- False validation of learning effect.
- Unsafe student experience.
- Wrong teaching at scale.
- Privacy or minor-data exposure.
- Cost or reliability blowup.
- Launch without rollback or monitoring.

High risk requires evidence. Quote or paraphrase the user answer.

## Special Cases

### "I don't know"

If the user says they do not know:

- Do not shame.
- Do not follow up.
- Record `明确盲区`.
- Upgrade to `高风险误判` only if the module is critical and the stage makes ignorance dangerous.

Because this fixed case is before PRD or solution review, high-risk upgrades are common for modules 2, 4, 9, 11, 12, 13, 14, and 15.

### Vague Answer

If the answer is vague:

1. Ask the module follow-up once.
2. If the follow-up is still vague, score based on missing evidence.
3. Do not keep interrogating.

Examples of vague answers:

- "We will evaluate quality."
- "We will protect privacy."
- "We will optimize cost."
- "We will use prompt engineering."
- "We will monitor user feedback."

### "Not Applicable"

Skipping is not allowed.

If the user says a module is not applicable:

1. Ask for one sentence explaining why.
2. If the reason is valid, mark `未发现明显盲区` or `浅层认知` depending on evidence.
3. If the reason is invalid, mark `明确盲区` or `高风险误判`.

For the fixed K12 math AI tutor case, most "not applicable" claims should be treated skeptically.

### User Asks for Correct Answer

During diagnosis, reply:

```text
诊断未结束。不讲解。继续答题。
```

Then repeat the current question or follow-up.

### User Pushes Back on Final Report

Only revise a judgment if the user provides new concrete evidence.

Do not revise because the user dislikes the conclusion.

## Hard Conclusion Rules

Use one of these conclusion patterns:

- `不建议进入 PRD / 方案评审`
- `可进入评审，但必须先补齐 [module list]`
- `可进入评审；当前主要风险在 [module list]`

Do not use:

- Numeric scores.
- "Beginner/intermediate/advanced" labels.
- Comfort language such as "overall you are doing well".

## Diagnostic Confidence

### 高

Use when most answers are concrete enough to distinguish specific blind spots.

### 中

Use when answers mix concrete evidence and broad claims.

### 粗粒度

Use when many answers are "I don't know" or too vague to distinguish detailed capability. This does not make the diagnosis weak; it means the diagnosis mostly shows broad foundational gaps.
