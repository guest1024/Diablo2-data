# 第一版检索问答流程与代码说明

本文补充说明当前第一版系统的执行流程、关键模块职责，以及多路召回 / 查询重写 / 子问题分解是如何落到代码里的。

## 1. 端到端执行流程

当前 `/qa` 的主流程可以概括为：

1. **query normalize**
2. **query analyze**
3. **entity resolve**
4. **multi-route retrieval**
5. **grounding decision**
6. **answer generation / fallback**

对应主入口在：

- `app/service.py`

核心路径：

```text
Diablo2QAService.answer()
  -> analyze_query()
  -> graph.resolve_entities()
  -> chroma.query_chunks_multi()
  -> _build_evidence_chunks()
  -> _collect_sources()
  -> answer_question() / _build_grounded_fallback_answer()
```

---

## 2. 查询归一化：`app/query_normalizer.py`

### 职责

- 对用户输入做空白归一化
- 按 `docs/tier0/bilingual-term-map.json` 做术语命中
- 返回：
  - `matched_terms`
  - `matched_entries`
  - `preferred_terms`
  - `canonical_hints`
  - `preferred_title_contains`
  - `preferred_text_contains`
  - `preferred_source_ids`

### 关键稳定性设计

#### 2.1 长词优先 / 嵌套命中抑制

例如：

- `新星电法` 不应先被 `电法` 吃掉
- `乔丹戒指` 不应只退化成宽泛的 `乔丹`

当前通过 `_matched_term_payloads()` 做：

- 先按词长降序筛选
- 再抑制已被更长词覆盖的短词

这是本轮保证“简称稳定、不串路由”的关键逻辑之一。

#### 2.2 source-aware 偏好提示

normalizer 会把 term-map 中的：

- `preferred_title_contains`
- `preferred_text_contains`
- `preferred_source_ids`

一起带到后续检索层，用于稳定把：

- `乔丹` -> `Stone of Jordan / 乔丹（Curated Anchor Card）`
- `超市` -> `Chaos Sanctuary / 超市（Curated Anchor Card）`

顶到正确位置。

---

## 3. 查询分析：`app/query_analyzer.py`

### 职责

将归一化后的 query 转成结构化检索计划，主要输出：

- `intent`
- `complexity`
- `needs_decomposition`
- `entity_query`
- `salient_facets`
- `rewritten_queries`
- `subquestions`
- `retrieval_plan`

### 设计原则

#### 3.1 规则优先，LLM 只做增强

当前不是“全靠大模型改写”。

而是：

- 简单/稳定问题：**纯规则分析**
- 中复杂问题：**规则结果 + 可选 LLM refinement**
- LLM 失败：**自动回退规则结果**

这样可以兼顾：

- 俗称/黑话稳定路由
- 子问题分解可控
- 外部 API 抖动时系统不崩

#### 3.2 facet-aware rewrite / decomposition

当前规则分析不只看 `intent`，还会抽取一层 `salient_facets`，把用户问题里真正影响召回的细节保留下来，例如：

- `Infinity + Scythe + Polearm + 4 socket`
- `Nova Sorceress + ES + Memory + Infinity Scythe`
- `Ancient Tunnels + Lost City`

这些 facet 会参与两件事：

1. 生成更贴近检索的 `rewritten_queries`
2. 生成更稳的 `subquestions`

这样多路召回不再只有“实体名 + 泛化 suffix”，而是能把真实玩家输入里的关键限定条件带进检索层。

#### 3.3 retrieval plan 明确化

系统不再只构造一个 expanded query，而是显式生成：

- original
- entity
- rewrite_*
- subquestion_*

每一路都带 `weight`，交给后续召回层并行检索。

---

## 4. 多路召回：`app/chroma_store.py`

### 当前召回通路

`query_chunks_multi()` 会融合三类通路：

1. **entity_link**
   - 图实体已足够确定时，直接把关联 chunk 提前召回
2. **lexical**
   - 对简称、黑话、中文俗称非常关键
3. **vector**
   - 覆盖语义近邻与表述变体

### 召回合并方式

每个 chunk 都会累计：

- `aggregate_score`
- `route_contributions`

这样能在结果里看到：

- 是哪一路 query 召回的
- 是 lexical 贡献更大，还是 vector / entity_link 更大

### curated anchor 稳定化

对于高价值中文俗称，当前会结合：

- `preferred_title_contains`
- `preferred_source_ids`

做 post-merge bonus，避免被宽泛列表页或噪声页面抢走 top1。

---

## 5. Grounding 与回答：`app/service.py`

### grounding mode

当前会在 `service.answer()` 中区分：

- `graph+evidence`
- `curated-evidence`
- `retrieval-only`

含义：

- **graph+evidence**：图实体可信，回答可带结构化 claims
- **curated-evidence**：实体不够稳，但 curated anchor 很稳，改走证据保守回答
- **retrieval-only**：只保留检索证据，不宣称图级 grounding

### LLM 失败保护

如果外部 LLM 回答失败：

- 不让 `/qa` 崩掉
- 自动走 `_build_grounded_fallback_answer()`
- 从 `claims / evidence_chunks / sources` 生成降级回答

---

## 6. OpenAI-compatible LLM 接入

相关文件：

- `app/config.py`
- `app/llm_client.py`

### 当前支持的环境变量

优先兼容两套命名：

- `LLM_API_KEY / LLM_BASE_URL / LLM_MODEL`
- `OPENAI_API_KEY / BASE_URL / MODEL`

因此你既可以继续沿用项目内命名，也可以直接使用：

```bash
export OPENAI_API_KEY="..."
export BASE_URL="https://.../api/v1"
export MODEL="gpt-5.4"
```

---

## 7. 为什么这套流程更清晰

相比“单 query -> 单 vector search -> 直接让 LLM 回答”的模式，现在的优势是：

1. **可解释**：每一步都有结构化输出
2. **可调试**：能看到 `query_analysis` 与 `route_contributions`
3. **可扩展**：后续能继续加 reranker、BM25、图查询层
4. **更稳**：简称/黑话/中文俗称不容易跑偏
5. **降级安全**：外部 LLM 不可用时仍能出 grounded fallback

---


## 9. Source-grounded Eval Dataset 方法

当前 `scripts/generate_llm_eval_dataset.py` 已改成 **基于仓库内 Diablo2 语料逐 seed 生成**，而不是让大模型脱离语料自由编题。

具体做法：

1. 每个 seed 先绑定 1~3 条仓库内真实证据 chunk
   - 例如 `docs/tier0/curated/chunks.jsonl`
   - 以及 `docs/chroma-ready/chunks.jsonl`
2. 把这些 chunk 的：
   - `title`
   - `source_id`
   - `keywords`
   - `reference_excerpt`
   明确塞进 prompt
3. 同时把目标约束一起塞给 LLM：
   - 目标 intent
   - 是否应触发 decomposition
   - query 必须包含的 alias / phrase
   - query 禁止包含的误导词
4. 最终把 `source_contexts / reference_titles / reference_keywords` 一并落盘到 dataset 中

并且现在额外提供自动验证脚本：

- `scripts/verify_llm_eval_dataset_grounding.py`

它会检查：

- 每个 seed 是否都在 dataset 中
- 每条 case 是否保留 `source_contexts / reference_titles / reference_keywords`
- query 是否仍满足 required term / required phrase 约束
- 最新 retrieval-only / llm-assisted 报告是否全绿

当前这套 dataset 已扩展成 **25 条 Diablo2 source-grounded case**，覆盖：

- routing：中文简称 / 黑话 / 区域俗称 / Runeword 缩写
- analysis：crafting_base / farming / location / usage / build

并且新增的 case 会专门检查：

- 主实体有没有稳定落到正确 canonical
- facet-aware rewrite 有没有把 `Memory` / `Infinity Scythe` / `Monarch` / `Lost City` 这类关键信号保留下来
- subquestion decomposition 有没有围绕同一主实体展开，而不是漂移到别的 build / boss / item

这样做的目的不是“让 eval 更好看”，而是让 eval 真正测到：

- Diablo2 俗称 / 黑话路由是否稳定
- 查询重写是否围绕真实实体表面词展开
- 子问题分解是否贴合真实 Diablo2 证据，而不是通用 LLM 发散

对于 `analysis_*` case，这一版数据集会更偏向：

- 底材选择
- 掉落 / farm 线索
- 位置 / 路线
- build / 配装

这些正好对应当前 `app/query_analyzer.py` 里的 intent 规则与多路召回计划。

## 8. 本轮重点验证过的稳定性问题

- `乔丹是什么？` -> `Stone of Jordan / 乔丹（Curated Anchor Card）`
- `乔丹戒指是什么` -> `entity_query = The Stone of Jordan Unique Ring`
- `新星电法是什么？` 不再被 `电法` 抢 top1
- `安达利尔是什么？` 不再被 `虫子` / `安头` 错抢 top1

这些都已经进入当前验证脚本与回归流程。
