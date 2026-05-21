# Report Template

Use this structure exactly enough to keep reports comparable. Fill with case-specific evidence.

```md
# AI PM 盲区诊断报告

## 硬结论

[不建议进入 PRD / 方案评审 | 可进入评审，但必须先补齐 X | 可进入评审，主要风险在 X]

一句话理由：[直接写最关键风险。]

## 诊断可信度

[高 | 中 | 粗粒度]

依据：[说明证据质量。若大量“不知道”，写：基础缺口广泛，无法做细粒度能力区分。]

## 最高风险盲区 Top 3

### 1. [模块名]

- 结论：[冷硬判断]
- 用户证据：[引用或转述用户回答]
- 缺失变量：[缺了哪些判断标准、约束、验证方法]
- 风险：[会怎样伤害 PRD、上线、安全、学习效果或商业结果]
- 最小补课动作：[一个最小行动，不给资源链接]

### 2. [模块名]

- 结论：
- 用户证据：
- 缺失变量：
- 风险：
- 最小补课动作：

### 3. [模块名]

- 结论：
- 用户证据：
- 缺失变量：
- 风险：
- 最小补课动作：

## 其他模块诊断

| 模块 | 等级 | 证据 | 风险 | 最小动作 |
|---|---|---|---|---|
| [模块] | [未发现明显盲区/浅层认知/明确盲区/高风险误判] | [短证据] | [短风险] | [短动作] |

## 反复暴露的认知模式

- [模式 1：例如把模型答对当成学生学会。]
- [模式 2：例如把上线当成验收终点。]
- [模式 3：例如把安全当成 prompt 写法问题。]

## 最小补课动作

1. [最高风险模块的一个动作]
2. [第二风险模块的一个动作]
3. [第三风险模块的一个动作]
```

## Writing Rules

- Use cold, direct language.
- Do not insult the user.
- Do not soften hard conclusions.
- Do not include external links.
- Do not include a numeric score.
- Do not add a motivational ending.
