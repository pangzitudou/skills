# EG 使用指南

Executable Governance（可执行治理）——让 AI agent 在写代码时不跑偏的一套关卡，外加把这套关卡变成一个命令行工具 `eg`。

> 一句话：把"意图 → 范围 → 行为 → 测试 → PR 闸"做成机器能校验的台阶，**结构交给 CLI，意义交给人**。每一步没填全，就过不去。

---

## 1. 为什么需要它

AI 写代码很能干，但会跑偏：自己脑补需求、跳过该做的步骤、漏掉边界情况。你回头审的时候，它已经在错的方向上写了一大片。

更早的一版工具有两个具体的痛：

- **每轮对话烧大量上下文在"手写 artifact"上**——agent 要把一大坨 YAML/JSON/Markdown 逐字敲出来。
- **漏填经常拖到最后一关（enforce）才暴露**——前面看着都"填了"，到 PR 评审才发现某个字段是占位符、某个文件根本没写。

挖到根上，第二个痛是这么来的：脚手架脚本写了个占位符 `TBD`，校验脚本只检查"字段非空"，于是 `"TBD"` 是非空字符串，**蒙混过关**。字段定义散在三个地方（脚手架、校验器、格式文档）各写一份，互相对不上。

EG 的答案：

- **单一真相**：每个产物的字段、必填、枚举、"什么算没填"只定义一次，scaffold / 校验 / 渲染全从它派生。`TBD` 这种占位符当场被拒。
- **可数完整性交给机器，意义交给人**：CLI 硬查"每个 symptom 有没有根因、每个 BDD 有没有边界场景、每个 ADR 有没有被覆盖"；人/agent 负责判断"这个根因成不成立、这个边界场景是真的还是凑数"。
- **数据为源，按需渲染**：产物以结构化数据（YAML）为提交源，人要看的 Markdown 视图按需渲染——agent 读数据更准，人读渲染更顺。

---

## 2. 心智模型

整条流水线四个阶段，按需进入（用户决定是否进 EG，进了之后按证据路由）：

```
  bug/问题          需求/意图           已批准意图            一个 PR
    │                 │                    │                    │
    ▼                 ▼                    ▼                    ▼
eg-diagnose ──▶ eg-precipitate ──▶     eg-tdd       ──▶    eg-enforce
找根因           沉淀意图/决策/约束     BDD→测试→实现        PR 闸
(只读·出证据)    →CONTEXT/ADR          →handoff→提交        (评审+判闸·不改码)
```

两条贯穿始终的原则：

1. **数据为源，按需渲染。** 提交进仓库的是 `.yml` 数据（`docs/adr/*.yml`、`docs/bdd/*.yml`、`CONTEXT.yml`）。给人看的 `.md` 是从数据渲染出来的，`.gitignore` 掉，不进 git。要看就 `eg render-all`。
2. **CLI 管可数完整性，人/agent 管意义。** 机器能数清楚的（字段填没填、边界场景有没有、引用对不对得上）由 CLI 硬卡；需要思考的（根因对不对、`Then` 是不是可观察行为）留给人。

还有一条贯穿的规矩：**硬闸 + 显式 defer**。没填的字段过不了闸；但你可以写 `defer: <原因>` 把它有意识地推迟——这样既不会静默漏掉，也不会被卡死。

### 运行态 vs 提交物

- **运行态**：每次跑都在 `/tmp/eg/<run-id>/` 下，放草稿数据、校验中间结果。**不进 git**。
- **提交物**：`docs/adr/*.yml`、`docs/bdd/*.yml`、`CONTEXT.yml`、`.eg/handoff/<run-id>.yml`。这些是仓库里的稳定契约。

---

## 3. 快速上手

### 调用方式

CLI 在 `skills/eg/cli/eg.py`。建议设个别名：

```bash
alias eg='python3 "$(readlink -f .agents/skills/eg)/cli/eg.py"'
# 之后就能直接 eg <命令>
```

下文都用 `eg` 指代它。

### 30 秒最小例子：沉淀一个 intent ADR

```bash
eg new precipitate --repo-root . --task reset-pw      # 开一个运行
eg adr-new <run> --type intent --title "Reset Password Flow"
cat <<'YAML' | eg merge <run> adr-0001                # 一次填一段语义
context: "用户会忘密码，需要自助重置。"
decision: "邮件重置，对未知邮箱也返回中性提示。"
in_scope:  ["邮件重置"]
out_of_scope: ["短信重置"]
non_goals: ["人工工单找回"]
acceptance_seed: ["未知邮箱返回中性提示", "过期链接无法改密"]
YAML
eg check <run> adr-0001                               # 漏了什么当场告诉你
eg seal  <run> adr-0001                               # 过闸 → 提交 docs/adr/0001-*.yml
```

`<run>` 是 `eg new` 打印出来的 run-id（形如 `EG-RUN-...`）或它的目录路径。

### 动词速查

| 通用 | 作用 |
|---|---|
| `eg new <stage> ...` | 开一个运行（diagnosis / precipitate / tdd / enforce） |
| `eg merge <run> <产物>` | 把一段 YAML 片段折进产物（**主力**，从 stdin 读） |
| `eg set <run> <产物> <路径> <值>` | 改单个标量 |
| `eg check <run> [产物]` | 报漏填和 defer 项 |
| `eg seal <run> [产物]` | 硬闸：校验过了才定稿/提交 |
| `eg render <run> [产物]` | 出人读预览（不动仓库） |
| `eg render-all <repo>` | 从 `.yml` 重新生成所有 `.md` |
| `eg lint <文件\|目录>` | 独立校验已提交的 `*.yml` 产物（无需 run 上下文，按 `schema` 路由） |
| `eg schema <产物>` | 现查字段和枚举，不用读格式文档 |

| 阶段专属 | 阶段 | 作用 |
|---|---|---|
| `eg adr-new` / `eg bdd-new` | precipitate / tdd | 领号 + 起草一个 ADR / BDD |
| `eg freeze` | tdd | 冻结 enforce-plan + ci-facts 契约 |
| `eg govern --phase planning\|final [--emit-handoff]` | tdd | 校验 ledger，final 时出 handoff |
| `eg commit-check --handoff <path>` | tdd | 校验暂存文件都在本次运行范围内 |
| `eg pr-context` / `eg select` | enforce | 取 PR diff / 选 handoff + 质量上下文 |
| `eg enforce [--facts <ci.json>]` | enforce | 跑闸：定级 + 判闸 + 更新 finding 台账 |
| `eg notify` / `eg fix-handoff` | enforce | 推送摘要 / 生成修复交接 |

---

## 4. 分阶段用法

### eg-diagnose —— 找根因（只读）

**干嘛**：把 bug/问题查成有证据的根因，绝不改代码、数据、配置。
**何时用**：有故障现象、要先搞清楚"为什么"再动手。

```bash
eg new diagnosis --repo <名字> --task <slug>
# 记录症状 + 来源矩阵（11 类来源，每类标 needed + 理由）
cat <<'YAML' | eg merge <run> diagnosis
symptoms:
  S1: { description: "重置接口高峰超时", status: explained }
YAML
cat <<'YAML' | eg merge <run> source-matrix
categories:
  code: { needed: true, reason: "定位连接池/重试路径", impact_if_missing: "找不到根因" }
  # ... 其余类别，需要就 true 不需要就 false，都要给理由
YAML
eg set <run> source-gap status complete
# 深入诊断：每个症状一条 problem_findings，带根因/证据/缺口/修复方向
eg check <run>          # 绿了才能 seal
eg seal  <run>          # 标记 diagnosis-complete，自动渲染预览
```

**闸的意义**：高置信根因要求直接证据或两类独立来源 + 来源缺口为 complete——CLI 硬卡，你仍要判断证据是否真支撑。

### eg-precipitate —— 沉淀意图（出 ADR / CONTEXT）

**干嘛**：把意图、范围、术语、决策、约束盘清楚，稳定了才写成 ADR / CONTEXT。
**何时用**：根因已知、要对齐"做什么、边界在哪、哪些决定不可逆"。

```bash
eg new precipitate --repo-root . --task <slug>
eg adr-new <run> --type intent|decision|constraint --title "..." [--domain security]
cat <<'YAML' | eg merge <run> adr-0001   # 见上面 30 秒例子
...
YAML
eg check <run> adr-0001
eg seal  <run> adr-0001                   # 提交 docs/adr/NNNN-*.yml（+ 渲染 ignored .md）
```

- **intent ADR** 才能往下喂给 tdd，且要有 `acceptance_seed`。批准前 `status: review`，人点头后 `eg set <run> adr-0001 status approved` 再 seal。
- **CONTEXT** 只放术语表：`eg merge <run> context` 填 `name/description/terms`，`eg seal <run> context` → `CONTEXT.yml`。

### eg-tdd —— 批准的意图 → BDD → 测试 → 实现 → 交接 → 提交

**干嘛**：把已批准的 intent 推成已批准的 BDD、验证过的测试、最小实现、仓库 handoff、一次范围内提交。
**何时用**：有一个 `approved` 的 intent ADR + Acceptance Seed。

```bash
eg new tdd --repo-root . --task <slug> --intent-adr ADR-0001 --mode lite
eg bdd-new <run> --title "Reset Password" --derived-from ADR-0001
cat <<'YAML' | eg merge <run> bdd-0001    # 每条 seed 至少 1 happy + 1 edge
scenarios:
  scenario-neutral: { title: "未知邮箱中性提示", kind: happy, given: ["x@y 未注册"], when: ["提交重置"], then: ["返回中性提示"] }
  scenario-expired: { title: "过期链接被拦", kind: edge,  given: ["链接过期"],   when: ["打开链接"], then: ["无法改密"] }
YAML
eg check <run> bdd-0001                    # CLI 卡"有没有 edge"，你自己过四问尺（是否可观察…）
eg set <run> bdd-0001 status approved      # 人批准后
eg seal <run> bdd-0001                     # 提交 docs/bdd/NNNN-*.yml + 盖批准元数据

# 冻结基线 → 写测试(RED→GREEN) → 校验 → 出 handoff
eg merge <run> ledger < ledger-fragment.yml
eg freeze <run>
eg govern <run> --phase planning
# ...（你写验收测试和对抗性假设，CLI 不替你写测试）...
eg govern <run> --phase final --emit-handoff   # 出 .eg/handoff/<run>.yml
eg commit-check <run> --handoff .eg/handoff/<run>.yml
```

> 提示：填 `ledger.touched_files` 时列**提交的 `.yml`**（如 `docs/bdd/NNNN-*.yml`），不是渲染的 `.md`。

### eg-enforce —— PR 时的外层闸

**干嘛**：从 handoff、CI facts、隔离评审里，报告闸结果 + 问一个下一步问题。**不改代码**。
**何时用**：一个 PR 要过 EG 闸。

```bash
eg new enforce --repo-root . --repo <名字> --target main
eg pr-context <run>      # 取 diff + PR 上下文
eg select   <run>        # 选活跃 handoff + 质量上下文
# 你跑隔离的评审 subagent，各写 layer-a-findings.json / layer-b-findings.json
eg check    <run>        # 守门：拦下畸形/占位的 finding
eg enforce  <run> --facts ci-facts.json   # 真正判闸 + 更新 finding 台账
eg notify   <run>        # 默认 dry-run 出摘要
```

**铁律**：评审只产出 finding，**只有 `eg enforce`（背后的 enforce.py）定级和判闸**。enforce 退出码 1 = 闸被拦（合法结果），2 = 输入契约错误（如 CI fact 缺/重，停下报告）。

---

## 5. 为什么这么设计

### 单一 schema registry —— 根除"TBD 蒙混过关"

老 bug：scaffold 写 `reason: "TBD"`，validator 只查"是不是非空字符串"，`"TBD"` 非空 → 过。字段定义散在脚手架/校验器/文档三份，必然漂移。
现在每个产物的字段/必填/枚举/"什么算没填"只定义一次，scaffold、merge、check、render 全派生。占位符（`TBD`/`todo`/`fixme`…）在写入时就被拒。**三处漂移 → 一处真相。**

### merge 为主 + 写入即校验 —— 一招治两痛

agent 不再整文件 Write，只发一段语义片段（`eg merge`），CLI 补结构、填默认、当场校验枚举和占位符。于是：
- **emit 成本 ↓**：不重复敲结构样板，也不用读格式文档（`eg schema` 现查）。
- **漏填提前**：值一写进去就校验，错的当场弹回。

### 数据为源 + `.md` gitignore + render-all —— 为什么不提交 `.md`

ADR/BDD/CONTEXT 的主要读者其实是 agent，读结构化数据更准、改起来更精确（`merge`/`set` 能精准打到字段），diff 也更干净。所以**提交的是 `.yml` 数据**。
那给人看的 `.md` 呢？**渲染出来，gitignore 掉，按需 `eg render-all` 再生**。为什么不放到 `/tmp` 镜像、保持仓库纯数据？因为有个硬约束：`validate-commit-scope` 要在**真 repo** 里跑 `git diff --cached`，没法指到一个 `/tmp` 副本——所以渲染的 `.md` 必须就地待在仓库树里（被 gitignore），不能搬走。

### wrap，不重写 —— 低风险复用强校验

tdd/enforce 那几个校验器（`validate-governance.py` 885 行、`enforce.py` 等）已经很强、很对。重写它们风险高、没必要。所以 `eg freeze`/`govern`/`commit-check`/`enforce` 都是**包一层**调它们；CLI 只在它们外面加授权（merge/set）、占位符守门、和"跑之前先 render-all 把 `.md` 从 `.yml` 生出来"。**一个新文件就够（`mirror.py`），其余复用。**

### 硬闸 + defer —— 抓漏但不死锁

光"能校验"不够——老问题就是校验靠自觉、agent 忘了跑。现在跳阶段/出 handoff 的命令**不过 check 就拒**，漏填物理上跨不了边界。但有些字段确实当下未知（缺证据、待定的 ADR），于是给一个逃生门：写 `defer: <原因>` 就放行，并在 `check` 里被列出来——**静默漏掉不行，有意识推迟可以**。

---

## 6. 速查参考

### 产物地图

| 产物 | 在哪 | 谁产出 |
|---|---|---|
| `source-matrix` / `source-gap` / `query-plan` / `diagnosis` | `/tmp/eg/<run>/`（运行态） | diagnose，merge/set |
| `context` / `adr-NNNN` | 草稿在 `/tmp`，seal 后 → `CONTEXT.yml` / `docs/adr/NNNN-*.yml`（提交） | precipitate |
| `bdd-NNNN` | 草稿在 `/tmp`，seal 后 → `docs/bdd/NNNN-*.yml`（提交） | tdd |
| `ledger` | `/tmp/eg/<run>/ledger.json`（运行态） | tdd，merge/set + 脚本 |
| `enforce-plan` / `ci-facts.contract` | `/tmp`（`eg freeze` 派生） | tdd |
| `.eg/handoff/<run>.yml` | 仓库（提交） | `eg govern --emit-handoff` |
| `findings` / `feedback` / `finding-ledger` / `fix-handoff` | `/tmp`（运行态） | enforce |

### 仓库布局

```
仓库/
├── CONTEXT.yml            ← 提交（源）        CONTEXT.md      ← 渲染·gitignore
├── docs/adr/NNNN-*.yml    ← 提交（源）        NNNN-*.md       ← 渲染·gitignore
├── docs/bdd/NNNN-*.yml    ← 提交（源）        NNNN-*.md       ← 渲染·gitignore
├── .eg/handoff/<run>.yml  ← 提交
└── .gitignore             ← 含 docs/adr/*.md, docs/bdd/*.md, /CONTEXT.md
```

`eg schema` 支持的产物：`source-matrix` `source-gap` `query-plan` `diagnosis` `context` `adr-intent` `adr-decision` `adr-constraint` `bdd` `findings`。

---

## 7. 常见问题 / 坑

**Q：PR 里看到的是 YAML 不是 Markdown？**
对。提交源就是 `.yml` 数据。要看人读版：`eg render-all .` 本地生成 `.md`，或 `eg render <run> <产物>` 出单个预览。

**Q：我手改了 `docs/adr/0001-x.md`，结果被覆盖了。**
`.md` 是渲染产物、不是源。改 `.yml`（或重新 `eg merge`/`eg set`），再 `eg render-all`。

**Q：刚 clone 下来没有 `.md`。**
正常——`.md` 不进 git。跑 `eg render-all .` 从提交的 `.yml` 生出来。tdd/enforce 的命令会自动先 render-all，所以脚本不受影响。

**Q：`ledger.touched_files` 该列哪个？**
列提交的 `.yml`（如 `docs/bdd/NNNN-*.yml`），不是 gitignore 的 `.md`。

**Q：某字段现在真填不了。**
`eg set <run> <产物> <路径> "defer: 等生产日志"`——放行但会在 `check` 里被点名，不会静默漏掉。

**Q：`eg check` 报"placeholder"。**
你写了 `TBD`/`todo`/`fixme` 之类占位符。换成真值，或用 `defer: <原因>`。

---

## 设计蓝图

完整的决策记录和构建过程见 `eg/REFACTOR-PLAN.md`。
