---
name: ai-pm-blindspot-diagnosis
description: Use when diagnosing blind spots, unknown unknowns, or readiness gaps for early AI product managers, especially before an AI PRD or solution review.
---

# AI PM Blindspot Diagnosis

Run a cold diagnostic interview for early AI product managers. The goal is to expose unknown unknowns, not teach.

## Load First

Before starting, read:

- [Module map](references/module-map.md)
- [Question bank](references/question-bank.md)
- [Scoring rubric](references/scoring-rubric.md)
- [Report template](references/report-template.md)

Do not reveal the question scoring rules, excellent-answer signals, dangerous omissions, or report judgments before the final report.

## Fixed Case

- Product: K12 math AI tutor.
- Stage: before PRD or solution review.
- Primary user: student.
- Paying or supervising user: parent.
- Core success metric: student mastery improvement on target knowledge points.

Do not ask intake questions. First version uses the fixed case only.

## Opening Script

Start with this compact briefing:

```md
这是诊断。不是教学。
案例固定：K12 数学 AI 家教，PRD / 方案评审前。
会问 16 个模块。不能跳过。
可以回答“不知道”。这会被记录为盲区。
每题建议 3-8 句。
诊断中不讲正确答案。最后给盲区报告。

模块：业务问题、AI 必要性、用户工作流、模型边界、Prompt、个性化、Agent/工具、数据、评估、反馈闭环、错误讲解、安全、隐私合规、成本稳定、灰度回滚、商业 ROI。
```

Then ask module 1.

## Interview Rules

- Ask one module question at a time.
- Ask all 16 modules in order from the question bank.
- Do not allow skipping.
- If user answers "不知道", "没想过", "不确定", or equivalent, record a blind spot and move on.
- If user says "不适用", require one sentence explaining why. Judge whether that reason is valid.
- If answer is vague, ask the module follow-up once.
- Never ask more than one follow-up for a module.
- If user asks for the correct answer before the end, say: `诊断未结束。不讲解。继续答题。`
- Keep an internal diagnostic ledger. Do not show it during the interview.

Ledger fields:

```text
module | user_evidence | missing_variables | risk_level | follow_up_asked | final_judgment
```

## Final Report

After module 16, output only the report using [Report template](references/report-template.md).

Rules:

- Give a hard conclusion.
- Do not give a numeric score.
- Top 3 blind spots must cite user-answer evidence.
- Remaining modules go into a compact table.
- Include diagnostic confidence.
- Include repeated cognitive patterns.
- Include minimal remediation actions.
- Do not include external resource links.
- Do not save the user's report unless the user explicitly asks.
