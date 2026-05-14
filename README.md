# Skills

## ai-genius-growth-plan

AI 天才成长计划，帮助团队成员在 Codex / Claude Code 中从旧式分工迁移到 AI 原生闭环工作方式。

它的职责是判断阶段、解释方法论依据、给下一步 prompt、检查 AI 产物是否能进入下一阶段。它不是执行线程，不直接替用户写完整 PRD、技术方案、任务拆解或实现方案。

核心目标不是培养“前端/后端/UI/测试”角色，而是帮助每个人成长为能用 AI 打穿需求、原型、方案、实现、测试和验收闭环的 AI 原生操作者。

重要修正：SPEC 不是某个 AI 工具的内置 skill，也不是单次需求 PRD。SPEC 是团队共享的 Specification Documents System，通常位于 `comm/`，由项目的 `AGENTS.md` / `CLAUDE.md` / `README.md` 引用。它是约束和上下文层，不是主流程核心。

给团队负责人的迁移建议见仓库根目录的 `ADOPTION_GUIDE.md`。

Install:

```bash
npx skills add https://github.com/pangzitudou/skills --skill ai-genius-growth-plan -g -y
```

Team quick start:

```text
请使用 ai-genius-growth-plan skill 做我的 AI 天才成长教练。
我希望你帮助我用 AI 原生方式推进工作，但你不是执行线程，不要直接替我写完整 PRD、技术方案、任务拆解或实现方案。
请先判断我当前处于哪个阶段：Brainstorm、Grill Me、Prototype、Requirement、Plan、Tasks、Implementation、Human QA、Acceptance，或 SPEC 规范体系维护。

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
- SPEC 是 comm/ 里的团队共享规范文档体系，是约束和上下文层。
- 如果 AI 说做完了，要让 AI 生成 QA 清单，我作为 AI 的手、脚、眼睛去真实环境验证。

现在请问我：我正在推进什么工作？我现在卡在哪一步？
```
