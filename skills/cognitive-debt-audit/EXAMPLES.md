# Examples

## Lightweight Audit

Input pattern:

- The user asked AI to summarize a video or article.
- The user did not provide their own prior model.
- The output became a note directly.

Useful response:

```text
审计结论：
这次主要债务不是“用了 AI”，而是你跳过了自己的第一版理解。

主要逃避点：
- Skipped modeling: 你直接让 AI 总结材料，但没有先写出自己认为文章在解决什么问题。

能力债：
- 主动建模。你需要练的是在接收答案前，先生成一个可被修正的粗模型。

还债动作：
- 不看 AI 总结，用 150 字写出这篇材料的核心论点、两个支撑点、一个你不确定的地方。
- 完成标准：写完后再对照 AI 总结，标记自己漏掉的点和 AI 过度解释的点。

下次观察：
- 下次让 AI 总结前，先问自己：我现在的粗理解是什么？
```

## Medium Audit

Input pattern:

- The user asked AI to compare options.
- AI recommended one option.
- The user accepted it without asking for failure modes.

Useful response:

```text
审计结论：
这次认知债集中在判断力：你获得了一个方案，但没有获得足够的选择理由。

主要逃避点：
- Skipped judgment: 对话里没有出现反例、边界条件、风险或替代方案比较。

能力债：
- 方案判断和边界意识。你需要能说清楚为什么选它，以及什么时候不该选它。

还债动作：
- 写出“我接受这个方案的 3 个理由”和“这个方案会失败的 2 个场景”。
- 完成标准：如果写不出失败场景，就回到原对话继续追问风险。

下次观察：
- 当 AI 给出推荐时，默认追问：这个建议在哪些条件下不成立？
```

## Deep Audit

Input pattern:

- The user used AI to complete a project plan or technical implementation.
- The result matters.
- The user feels the output is done but cannot explain or reproduce it.

Useful response:

```text
审计结论：
这次不是单一逃避点，而是“完成感”跑在“理解感”前面了。

主要逃避点：
- Skipped reconstruction: AI 给出了完整流程，但你没有关闭对话后独立复述。
- Skipped consolidation: 对话结束后没有留下原则、检查清单或下次复用模板。

能力债：
- 独立复现和结构化记忆。你需要把 AI 的一次性帮助改造成自己的可复用能力。

还债动作：
- 关闭对话，重写一份 7 步以内的个人执行清单。
- 用一个相似但更小的案例复现流程。
- 提炼 1 条原则和 1 个下次提问模板。

完成标准：
- 你能不用原对话解释为什么每一步存在。
- 你能指出其中一步如果省略会造成什么问题。

下次观察：
- 当 AI 输出完整方案时，不急着保存，先问：我能不能不用它复述一遍？
```
