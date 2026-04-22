# Ralph Handoff - 2026-04-22

> 目标：把当前 Diablo2 第一版 RAG / 检索问答系统的工作进展、设计思路、验证证据、后续优化路线完整记录下来，方便下一次直接续跑。

---

## 1. 当前结论（可直接看）

本轮已经完成以下关键工作，并且核心验证全部为绿色：

1. **补强了 query analyzer**
   - 新增 `salient_facets`
   - 新增 **facet-aware query rewrite**
   - 新增 **facet-aware subquestion decomposition**
   - 收紧了 LLM merge 的漂移边界
   - 修复了 `usage` 与 `crafting_base` 的一部分规则冲突

2. **把 Diablo2 source-grounded eval dataset 从 14 条扩充到 25 条**
   - 严格基于仓库内 Diablo2 语料生成
   - 不再是通用 LLM 自由出题
   - 新增了 HOTO / CTA / 劳模 / 牛场 / 古代通道 / 虫子 等黑话与缩写覆盖

3. **补强了外部 LLM 调用韧性**
   - `app/llm_client.py` 增加了 429 / timeout / connection / 5xx 的退避重试
   - `scripts/generate_llm_eval_dataset.py` 增加了单 seed API 失败重试与 fallback 逻辑

4. **文档已同步更新**
   - `docs/first-system-flow-and-code.md`
   - `docs/first-system-quickstart.md`
   - 本交接文档：`docs/ralph-handoff-2026-04-22.md`

5. **最新验证状态**
   - `verify_query_analysis_contract.py`：PASS
   - `verify_grounding_contract.py`：PASS
   - `verify_llm_execution_path.py`：PASS
   - `verify_llm_eval_dataset_grounding.py`：PASS
   - `verify_first_system_stack.py`：**14 / 14 PASS**
   - retrieval-only eval：**25 / 25 PASS**
   - llm-assisted eval：**25 / 25 PASS**

---

## 2. 本轮具体做了什么

### 2.1 QueryAnalyzer 设计补强

文件：`app/query_analyzer.py`

本轮的核心变化不是简单“多加几条 rewrite”，而是把查询分析从：

- `intent + entity_query`

推进为：

- `intent + entity_query + salient_facets + rewrites + subquestions`

#### 新增的关键能力

##### A. `salient_facets`

用于保留用户原问题里真正会影响召回质量的细节。

典型例子：

- `Infinity + Scythe + Polearm + 4 socket`
- `Nova Sorceress + ES + Memory + Infinity Scythe`
- `Spirit Shield + Monarch + 军团圣盾`
- `Ancient Tunnels + Lost City`

##### B. facet-aware rewrite

以前 rewrite 更偏“实体名 + 通用 suffix”，例如：

- `Nova Sorceress build gear skill setup`

现在会把真正关键的 facet 带进去，例如：

- `Nova Sorceress Memory Infinity Scythe`
- `Infinity Scythe Polearm`
- `Spirit Shield 底材 Monarch`

这样多路召回更容易把：

- build 限定条件
- base / socket 限定条件
- 路线入口限定条件

一起带进 lexical / vector / entity-linked 路由。

##### C. facet-aware subquestions

以前 subquestion 更泛化；
现在会尽量围绕同一主实体，把 facet 保留下来。

例如：

- `Nova Sorceress 在 Memory / Infinity Scythe 这类设定下通常怎么配装或加点？`
- `Infinity 用 Scythe / Polearm 做底材或孔数要求要注意什么？`

##### D. LLM merge guardrails

LLM 现在不是“自由重写”，而是：

- 规则结果先出
- LLM 只做保守增强
- merge 时再过滤：
  - 不能丢主实体
  - 不要引入明显漂移 query
  - 结果长度受控

##### E. usage / crafting_base 冲突修复

曾经出现过类似：

- `牛场有啥用，适合刷底材和刷符文吗？`

被错误打成 `crafting_base`。

现在新增了一个更保守的优先规则：

- 如果问题明显是 `有啥用 / 用途 / 适合` 语义
- 且没有强 crafting 信号（如 `几孔 / Monarch / Polearm / Scythe / 符文之语`）
- 则优先归入 `usage`

---

### 2.2 Diablo2 source-grounded eval 扩容

文件：`scripts/generate_llm_eval_dataset.py`

之前 eval 已经从“通用 prompt 出题”改成“基于仓库证据逐 seed 生成”。
本轮继续把它扩充到 **25 条 case**。

#### 当前覆盖结构

##### Routing（14 条）

覆盖：

- Spirit
- Shako / 军帽
- Hellfire Torch / 火炬
- SOJ / 乔丹
- Infinity / 无限
- Chaos Sanctuary / 超市
- Nova Sorceress / 新星电法
- Countess / 女伯爵
- HOTO / 橡树之心
- CTA / 战争召唤
- Mephisto / 劳模
- Secret Cow Level / 牛场
- Ancient Tunnels / 古代通道
- Andariel Bug / 虫子

##### Analysis（11 条）

覆盖 intent：

- `crafting_base`
- `farming`
- `location`
- `usage`
- `build`

重点覆盖：

- Spirit Shield base
- Harlequin Crest farm
- Chaos Sanctuary path
- The Pit usage
- Infinity base
- Nova Sorceress build
- HOTO usage
- CTA usage
- Mephisto farm
- Ancient Tunnels location
- Cow Level usage

#### 设计原则

每个 seed：

- 绑定真实 `curated` / `chroma-ready` chunk
- 生成 prompt 时显式塞入：
  - `title`
  - `source_id`
  - `keywords`
  - `reference_excerpt`
- 同时塞入硬性约束：
  - `expected_intent`
  - `required_query_terms_any`
  - `required_phrase_any`
  - `avoid_terms`
  - `prompt_goal`

因此 dataset 是“**Diablo2 语料约束下的 query eval**”，不是“通用知识问答”。

---

### 2.3 LLM 调用韧性补强

文件：

- `app/llm_client.py`
- `scripts/generate_llm_eval_dataset.py`

本轮命中过一次真实 429：

- `Too many pending requests, please retry later`

因此做了两层防护：

#### A. llm_client 统一重试

`chat_completion()` 现在对以下情况做退避重试：

- `RateLimitError`
- `APITimeoutError`
- `APIConnectionError`
- `InternalServerError`

#### B. dataset generator 单 seed 失败不直接崩

`generate_case()` 现在会：

- 捕获单次 API 失败
- 继续 retry
- 最后如果 seed 配了 fallback，就安全落到 fallback query

这能显著降低批量 eval 生成时因为外部 API 波动导致整批任务失败的概率。

---

## 3. 当前验证证据

### 3.1 Query analysis contract

`python3 scripts/verify_query_analysis_contract.py`

已验证：

- 实体 query 稳定
- retrieval plan 保留关键 facet
- subquestions 保留关键 facet
- 不依赖外部 LLM 也能稳定出结构化分析

重点例子：

- `精神盾底材是什么` -> retrieval plan 保留 `Spirit Shield` + `Monarch`
- `新星电法 ... Memory ... Infinity Scythe ...` -> retrieval plan / subquestion 同时保留 `Memory` + `Infinity Scythe`

### 3.2 Eval reports

#### retrieval-only

文件：`docs/tier0/evals/llm-generated-query-eval-report-retrieval-only.json`

结果：

- `25 / 25 PASS`
- routing: `14 / 14`
- analysis: `11 / 11`

#### llm-assisted

文件：`docs/tier0/evals/llm-generated-query-eval-report-llm-assisted.json`

结果：

- `25 / 25 PASS`
- routing: `14 / 14`
- analysis: `11 / 11`

### 3.3 Grounding / execution

已通过：

- `scripts/verify_grounding_contract.py`
- `scripts/verify_llm_execution_path.py`
- `scripts/verify_llm_eval_dataset_grounding.py`

### 3.4 Full suite

文件：`docs/tier0/verification/verification-suite.json`

结果：

- `14 / 14 PASS`

---

## 4. 当前重要文件清单

### 核心实现

- `app/query_analyzer.py`
- `app/llm_client.py`
- `app/service.py`
- `app/chroma_store.py`
- `app/config.py`

### Eval / verification

- `scripts/generate_llm_eval_dataset.py`
- `scripts/evaluate_llm_generated_dataset.py`
- `scripts/verify_llm_eval_dataset_grounding.py`
- `scripts/verify_query_analysis_contract.py`
- `scripts/verify_grounding_contract.py`
- `scripts/verify_llm_execution_path.py`
- `scripts/verify_first_system_stack.py`

### 文档

- `docs/first-system-flow-and-code.md`
- `docs/first-system-quickstart.md`
- `docs/ralph-handoff-2026-04-22.md`

### 产出物

- `docs/tier0/evals/llm-generated-query-eval-dataset.json`
- `docs/tier0/evals/llm-generated-query-eval-dataset.md`
- `docs/tier0/evals/llm-generated-query-eval-report-retrieval-only.json`
- `docs/tier0/evals/llm-generated-query-eval-report-llm-assisted.json`

---

## 5. 详细思路：为什么这样做

### 5.1 为什么不是“全交给 LLM 改写”

因为这个系统目标不是一般问答，而是 **Diablo2 黑话 / 简称 / 多路召回 / GraphRAG grounding**。

如果把查询重写完全交给 LLM，会有几个问题：

1. **主实体漂移**
   - `Infinity 底材` 很容易漂到 `Nova Sorceress`
2. **intent 漂移**
   - `build` 很容易被写成 `location`
3. **eval 不可复现**
   - 大模型每次都可能换问法
4. **外部 API 波动影响主链路稳定性**

所以现在的策略是：

- **规则优先**
- **LLM 增强**
- **结果再过滤**

这是当前阶段更适合工程化落地的方案。

### 5.2 为什么要做 source-grounded eval

因为如果 eval query 本身不是从仓库语料里长出来的，那么你测到的就不是这个 RAG 系统本身，而是“LLM 随便造出来的问题能不能凑巧被答中”。

现在这套 eval 直接绑定仓库 chunk，才真正能测到：

- alias / slang routing
- rewrite 是否保留关键限定词
- decomposition 是否围绕同一实体
- grounding 是否走对层级

### 5.3 为什么要单独记录 `salient_facets`

因为后续很多优化都会复用它：

- retrieval route budgeting
- lexical boost
- reranker features
- answer planning
- eval diagnostics

这相当于给 query analysis 增加了一个“可解释中间层”。

---

## 6. 下一步最值得继续做的优化

下面按优先级写。

### P0：继续增强 query analysis 的稳定性

#### 方向

1. **intent 置信度 / conflict resolver**
   - 当前仍是 rule-first + 少量 heuristic
   - 下一步建议输出：
     - `intent_candidates`
     - `intent_confidence`
     - `conflict_reason`

2. **facet 分类**
   - 现在 `salient_facets` 还是扁平列表
   - 建议升级成：
     - `entity_facets`
     - `constraint_facets`
     - `route_facets`
     - `build_facets`

3. **subquestion 模板更细化**
   - 当前已经比之前稳定，但仍是模板驱动
   - 下一步可按 intent 拆到更细：
     - `crafting_base/base-vs-sockets`
     - `location/entry-vs-route`
     - `usage/use-case-vs-target-build`
     - `build/core-gear-vs-buff-tech`

#### 实施建议

- 新建一个中间结构，例如：
  - `query_analysis['facet_map']`
- 再由 `facet_map -> retrieval_plan`
- 再由 `facet_map -> subquestions`

这样未来调试会更容易。

---

### P1：把 retrieval 做成更像正式 RAG 的 hybrid pipeline

#### 当前状态

当前已经有：

- entity-linked
- lexical
- vector
- post-merge bonus

#### 下一步建议

##### 1. route-specific top_k / budget

当前每一路 query 基本是统一 top_k。
建议按路由类型做预算：

- `entity`：低 top_k，高权重
- `rewrite`：中 top_k
- `subquestion`：更保守 top_k

##### 2. lexical feature 更细化

目前 lexical 还比较朴素。
可加入更多显式特征：

- title exact hit
- keyword exact hit
- canonical alias exact hit
- source authority prior
- curated-anchor prior
- bilingual alias overlap

##### 3. reranker

当前 merge 还是基于 route score 聚合。
建议下一步加一个轻量 reranker 层：

输入特征可包括：

- entity exactness
- title match
- keyword overlap
- facet overlap
- route diversity
- source authority
- curated bonus

即使先不用 cross-encoder，也可以先做一个 feature-based rerank baseline。

---

### P2：Graph grounding 继续深化

#### 当前状态

已经区分：

- `graph+evidence`
- `curated-evidence`
- `retrieval-only`

#### 下一步建议

##### 1. entity resolution confidence 更显式

建议在输出里补：

- `entity_resolution_confidence`
- `entity_resolution_margin`
- `entity_resolution_reason`

##### 2. claim selection 更细粒度

当前 graph grounding 偏“实体命中后取 claims”。
下一步建议加：

- claim-predicate filtering
- intent-aware claim filtering
- facet-aware claim filtering

比如：

- `crafting_base` 优先取 sockets/base/requirements claim
- `location` 优先取 area/act/path claim
- `usage` 优先取 use-case / target-build / role claim

##### 3. provenance 去噪

后续可以继续压低“命中实体但 claim 噪声偏多”的情况，尤其是：

- alias 近似实体
- 同源长列表页
- 泛化 wiki 页面

---

### P3：答案生成层优化

#### 当前状态

- 有 grounding-aware fallback
- LLM answer 要求引用来源

#### 下一步建议

1. **answer plan 中显式带 intent**
2. **按 intent 决定答案结构**
   - definition：定义 + 关键属性 + 来源
   - farming：常见掉落点 / 场景 + 来源
   - location：入口 / 路线 + 来源
   - build：核心配装 / buff 技术 / 风险点 + 来源
3. **引用格式统一**
4. **证据不足时更明确指出缺口**

---

### P4：Eval / Observability 继续扩大

#### 建议方向

1. 从 25 条扩到 **40~60 条**
2. 每个 intent 至少有：
   - 中文简称 case
   - 中英混合 case
   - 黑话 case
   - facet-rich case
3. 增加以下 bucket：
   - alias ambiguity
   - intent conflict
   - entity drift risk
   - graph grounding suppression
   - curated-anchor preference
4. 增加错误快照材料：
   - bad rewrite samples
   - bad subquestion samples
   - top1 / top3 retrieval drift cases

---

## 7. 下一次建议的执行顺序

如果下次继续开发，建议按这个顺序：

### Step 1
先读：

- `docs/ralph-handoff-2026-04-22.md`
- `docs/first-system-flow-and-code.md`

### Step 2
先跑验证，确认基线：

```bash
python3 scripts/verify_query_analysis_contract.py
python3 scripts/verify_grounding_contract.py
python3 scripts/verify_llm_eval_dataset_grounding.py
python3 scripts/verify_first_system_stack.py
```

### Step 3
开始做 P0 / P1 中的一项，不要同时发散

推荐优先项：

- `facet_map` 结构化
- retrieval reranker baseline
- eval dataset 扩到 40+

### Step 4
每做完一轮修改，都重跑：

```bash
python3 scripts/generate_llm_eval_dataset.py
python3 scripts/evaluate_llm_generated_dataset.py
python3 scripts/evaluate_llm_generated_dataset.py --use-llm
python3 scripts/verify_llm_eval_dataset_grounding.py
```

---

## 8. 本轮遗留风险 / 注意事项

1. **外部 LLM endpoint 仍可能限流**
   - 虽然现在有 retry
   - 但大批量 eval 仍可能比较慢

2. **query analyzer 仍是规则主导**
   - 适合当前阶段稳定性
   - 但 recall ceiling 还没到头

3. **hybrid retrieval 还没有真正 reranker**
   - 当前 merge 结果已经能工作
   - 但还不是最终形态

4. **graph claims 还没做 intent-aware predicate filtering**
   - 这是后续 grounding 质量提升的大头之一

---

## 9. 恢复运行时的关键信息

### 当前 LLM 环境约定

项目已经兼容两套变量：

- `OPENAI_API_KEY / BASE_URL / MODEL`
- `LLM_API_KEY / LLM_BASE_URL / LLM_MODEL`

当前 `.env.local` 已按用户要求配置为：

- `OPENAI_API_KEY=...`
- `BASE_URL=https://vibediary.app/api/v1`
- `MODEL=gpt-5.4`

### 当前最重要的成功指标

- retrieval-only eval：`25 / 25`
- llm-assisted eval：`25 / 25`
- verification suite：`14 / 14`

如果下次续跑，**先保证这三个指标不回退**。

---

## 10. 一句话交接

当前系统已经从“第一版能跑”推进到了“**Query Analysis 更稳定、Diablo2 source-grounded eval 更完整、全链路验证可复现**”的状态；下一步最值得做的是 **facet_map 结构化 + reranker baseline + 更大规模 Diablo2 eval 扩展**。
