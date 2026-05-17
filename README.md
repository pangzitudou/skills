# Skills

## spec-driven-ai-workflow-coach

AI 辅助交付流程阶段门，帮助团队成员在 Codex / Claude Code 中判断需求、原型、SPEC、方案、实现、人工 QA 和验收之间的阶段边界。

它的职责是判断阶段、解释方法论依据、给下一步 prompt、检查 AI 产物是否能进入下一阶段。它不是执行线程，不直接替用户写完整 PRD、技术方案、任务拆解或实现方案。

核心目标不是回答所有 AI 协作、个人成长或团队转型问题，而是收窄到 AI 辅助交付流程：需求、原型、SPEC、方案、实现、测试和验收。

重要边界：SPEC 是合同，不是说明书。项目或功能 SPEC 记录目标、角色、范围、流程、规则、边界和验收；公司或公共 SPEC 沉淀跨项目可复用规则。README、API、架构、数据模型、测试、部署等内容各有职责，不要塞进 SPEC。

给团队负责人的迁移建议见仓库根目录的 `ADOPTION_GUIDE.md`。

## Usage Modes

### 1. Coach Thread Mode

默认模式。最可移植。

适合在任何 AI agent 中做阶段判断、SPEC 归位、人类接入判断、下一步建议。

如果上下文不足，让用户提供最小 Context Packet：

- 目标
- 当前阶段
- 已有产物
- 已做决定
- 未决问题
- 已有证据
- 想判断的 gate

### 2. Claude Code `/btw` Sidecar Mode

只用于基于当前对话上下文的快速判断。

适合判断：

- 当前阶段
- 下一步动作
- 内容应不应该进 SPEC
- 是否大概率需要 human gate

不要在这些情况使用 `/btw`：

- 需要读文件
- 需要搜索代码
- 需要运行命令
- 需要检查新产物
- 需要产出 review 证据

### 3. Tool-Enabled Review Mode

当判断需要工具证据时，使用主线程或 subagent。

适合：

- 读取 SPEC
- 读取代码
- 检查 git diff
- 运行测试
- 检查日志
- 产出 review evidence

Install:

```bash
npx skills add https://github.com/pangzitudou/skills --skill spec-driven-ai-workflow-coach -g -y
```

Team quick start:

```text
请使用 spec-driven-ai-workflow-coach skill 帮我判断 AI 辅助交付流程阶段。
我希望你帮助我判断工作能否进入下一阶段，但你不是执行线程，不要直接替我写完整 PRD、技术方案、任务拆解或实现方案。
请先判断我当前处于哪个阶段：Brainstorm、Grill Me、Prototype、SPEC、Plan、Tasks、Implementation、Human QA、Acceptance，或公共规范维护。

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
- SPEC 是合同，不是说明书；只放目标、角色、范围、流程、规则、边界和验收。
- README / API / DATA_MODEL / TESTING / DEPLOYMENT 各有职责，不要把命令、字段、代码、测试和部署细节塞进 SPEC。
- 如果 AI 说做完了，要让 AI 生成 QA 清单，我作为 AI 的手、脚、眼睛去真实环境验证。

现在请问我：我正在推进什么工作？我现在卡在哪一步？
```
