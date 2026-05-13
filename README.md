# Skills

## cognitive-debt-audit

AI 对话认知债审计，用来复盘导出的 AI 对话，识别你在学习、判断、复现和沉淀中绕开的困难，并把它们转成小的还债动作。

它的职责是把“AI 帮我完成了”改写成“我学会了什么、我跳过了什么、下一次要补什么”。它不反对使用 AI，也不在对话当场打断节奏；它只做事后审计。

Install:

```bash
npx skills add https://github.com/pangzitudou/skills --skill cognitive-debt-audit -g -y
```

Quick start:

```text
请使用 cognitive-debt-audit skill 审计下面这段 AI 对话。

我的目标不是减少 AI 使用，而是找出我在学习、判断、复现或沉淀中绕开的地方。

请输出：
1. 一句话审计结论
2. 1-3 个主要逃避点，附对话证据
3. 对应的能力债
4. 每笔债一个 5-30 分钟内能完成的还债动作
5. 下次使用 AI 时要观察什么

对话如下：
[粘贴导出的 AI 对话]
```

## ai-genius-growth-plan

AI 天才成长计划，帮助团队成员在 Codex / Claude Code 中从旧式分工迁移到 AI 原生闭环工作方式。

它的职责是判断阶段、解释方法论依据、给下一步 prompt、检查 AI 产物是否能进入下一阶段。它不是执行线程，不直接替用户写完整 PRD、技术方案、任务拆解或实现方案。

核心目标不是培养“前端/后端/UI/测试”角色，而是帮助每个人成长为能用 AI 打穿需求、原型、方案、实现、测试和验收闭环的 AI 天才。

给团队负责人看的迁移建议见仓库根目录的 `ADOPTION_GUIDE.md`。

Install:

```bash
npx skills add https://github.com/pangzitudou/skills --skill ai-genius-growth-plan -g -y
```

Team quick start:

```text
请使用 ai-genius-growth-plan skill 做我的 AI 天才成长教练。

我希望你帮助我用 AI 原生方式推进工作，但你不是执行线程，不要直接替我写完整 PRD、技术方案、任务拆解或实现方案。

请先判断我当前处于哪个阶段：Brainstorm、Grill Me、Prototype、SPEC、Plan、Tasks、Implementation、Human QA、Acceptance。

你的回答请固定包含：
1. 当前阶段
2. 为什么是这个阶段
3. 下一步我该做什么
4. 可以复制给执行线程的 prompt
5. 我拿到产物后应该怎么检查

请特别提醒我：
- 以需求为中心，不要被技术偏好或历史实现绑架。
- 做加法前，先做减法。
- 如果涉及界面、流程或操作，优先用快速 HTML 原型验证。
- 如果 AI 说做完了，要让 AI 生成 QA 清单，我作为 AI 的手、脚、眼睛去真实环境验证。

现在请问我：我正在推进什么工作？我现在卡在哪一步？
```
