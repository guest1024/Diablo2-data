# PostgreSQL 统一检索数据库设计

> 更新时间：2026-04-23  
> 目标：把当前 Diablo II 数据与后续数据字典，统一落到 PostgreSQL 的 **BM25 + embedding + graph expansion** 检索架构里。  
> 本文偏向：**当前适配落地的数据库设计文档**。

---

## 1. 设计目标

本数据库设计的目标是让 PostgreSQL 同时承担以下角色：

1. **外置向量数据库**：作为 embedding/vector store。
2. **BM25 / lexical 检索引擎**：作为传统关键词检索底座。
3. **别名 / 黑话 / 错拼规范化引擎**：作为 query normalization 的核心数据层。
4. **轻量知识图谱引擎**：通过关系表、递归查询、路径缓存支持多跳扩展。
5. **数据字典主存储**：承载后续的结构化事实、实体字典、术语字典、build 字典、规则字典。

### 不追求的事情

- 不要求数据库层必须暴露 Neo4j/Cypher 语法。
- 不要求数据库层自行完成所有机器学习推理。
- 不把 JSONB 当成一切事实的唯一承载方式。

---

## 2. 当前仓库的基础与现状

### 2.1 已有主数据层

当前主入口已经比较明确：

- `docs/tier0/merged/normalized/documents.jsonl`
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`
- `docs/tier0/alias-registry.jsonl`
- `docs/tier0/build-archetypes.jsonl`

### 2.2 已补充的结构化支持层

当前仓库已经新增：

- `docs/tier0/structured/base-items.jsonl`
- `docs/tier0/structured/runes.jsonl`
- `docs/tier0/structured/runewords.jsonl`
- `docs/tier0/structured/unique-items.jsonl`
- `docs/tier0/structured/skills.jsonl`
- `docs/tier0/structured/cube-recipes.jsonl`
- `docs/tier0/structured/areas.jsonl`
- `docs/tier0/structured/monster-resistances.jsonl`
- `docs/tier0/structured/breakpoints.jsonl`

### 2.3 已有 PostgreSQL 骨架

当前仓库已经落了一版 PG 骨架：

- `sql/postgres/001_core_schema.sql`
- `sql/postgres/002_optional_vector.sql`
- `sql/postgres/003_views.sql`
- `sql/postgres/queries.sql`
- `docs/tier0/postgres-bundle/`

这说明：
- **第一版“PG 能力验证版”已经存在**
- 但还需要进一步演进成统一检索数据库设计

---

## 3. 总体设计：六层模型

建议把 PostgreSQL 里的逻辑分成六层，而不是所有内容混成一个 schema。

### Layer A：`raw`
原始抓取 / 原始文件 / 原始 JSON。

### Layer B：`core`
规范化实体、关系、事实、来源、版本、冲突。

### Layer C：`search`
文档、chunk、BM25、trigram、embedding、query normalization。

### Layer D：`graph`
图扩展、邻接关系、多跳路径、物化视图。

### Layer E：`dict`
数据字典、术语字典、别名字典、规则字典、build 字典。

### Layer F：`ops`
ingest run、query log、retrieval trace、评测数据。

---

## 4. 当前落地推荐的 schema 设计

> 注意：这里的重点不是为了“把 schema 拆得很复杂”，而是为了后续数据字典、检索链路、评测链路可以持续扩展。

### 4.1 `core` 层

#### `core.entities`
实体主表。

建议字段：
- `entity_id`
- `entity_type`
- `canonical_name`
- `canonical_name_zh`
- `status`
- `game_variant`
- `patch_version`
- `source_priority`
- `props jsonb`

#### `core.aliases`
别名主表。

建议字段：
- `alias_id`
- `entity_id`
- `alias`
- `alias_type`
- `language`
- `confidence`
- `source`

#### `core.facts`
结构化事实表。

建议字段：
- `fact_id`
- `subject_id`
- `predicate`
- `value_text`
- `value_num`
- `value_jsonb`
- `unit`
- `source_id`
- `version_tag`
- `authority_tier`

#### `core.edges`
关系边表。

建议字段：
- `edge_id`
- `subject_id`
- `predicate`
- `object_id`
- `weight`
- `source_id`
- `authority_tier`
- `version_tag`
- `props jsonb`

### 为什么要 facts / edges 分离

因为：
- `Enigma -> USES_RUNE -> Ber` 是关系边
- `Spirit -> FCR range = 25..35` 是结构化事实

如果全塞进一个 JSONB 表，后续查询和优化都会变差。

---

### 4.2 `search` 层

#### `search.documents`
文档级检索主表。

建议字段：
- `doc_id`
- `source_id`
- `title`
- `language`
- `authority_tier`
- `content_type`
- `patch_version`
- `text_content`
- `metadata jsonb`

#### `search.chunks`
chunk 级检索主表。

建议字段：
- `chunk_id`
- `doc_id`
- `chunk_index`
- `text_content`
- `normalized_text`
- `language`
- `authority_tier`
- `search_weight`
- `metadata jsonb`

#### `search.chunk_fts`
如果希望更清晰地把 lexical lane 独立出来，可以把 FTS/BM25 派生列单独维护。

建议字段：
- `chunk_id`
- `text_search_config`
- `search_vector`
- `lexical_text_zh`
- `lexical_text_en`
- `lexical_text_mixed`

#### `search.chunk_embeddings`
建议把 embedding 单独拆表，避免和事务主表强耦合。

建议字段：
- `chunk_id`
- `embedding_model`
- `embedding vector(...)`
- `embedding_dim`
- `created_at`

#### `search.query_alias_rules`
作为 query rewrite / expansion 层。

建议字段：
- `rule_id`
- `query_term`
- `canonical_hint`
- `expanded_terms jsonb`
- `preferred_source_ids jsonb`
- `preferred_title_contains jsonb`
- `preferred_text_contains jsonb`

---

### 4.3 `graph` 层

如果不使用 AGE，也完全可以在 PG 中支持图扩展。

#### `graph.edges`
与 `core.edges` 可以是同源视图，也可以单独存储 graph-ready 的投影边。

#### `graph.entity_neighbors_mv`
物化视图，用于加速常用 1-hop/2-hop 查询。

#### `graph.entity_paths`
用 `ltree` 或预计算路径缓存保存高频层级路径。

适合：
- 技能树前置
- 场景层级
- build 依赖路径

---

### 4.4 `dict` 层（后续数据字典落地重点）

### 4.5 `qu` 层（Query Understanding）

这一层专门保证“输入理解 -> rewrite -> 子问题拆解 -> 检索计划”是可追踪、可调优、可验证的。

建议核心表：
- `qu.query_sessions`
- `qu.query_rewrites`
- `qu.query_rewrite_terms`
- `qu.entity_resolution_candidates`
- `qu.subquestion_plans`
- `qu.subquestion_steps`
- `qu.retrieval_policies`
- `qu.retrieval_plan_lanes`
- `qu.answer_constraints`

这层要解决的核心问题：

1. 用户原始输入是否被正确归一化
2. rewrite 是否只扩 recall、不明显伤 precision
3. 哪些 query 需要拆子问题
4. 哪些 query 必须启用 numeric/rule lookup
5. 哪些 query 最终必须走 citation verification gate

### 4.6 `qa` 层（Answer Quality / Citation Verification）

这一层专门保证“召回结果是否可靠、最后答案是否正确引用”。

建议核心表：
- `qa.retrieval_runs`
- `qa.retrieval_lane_hits`
- `qa.evidence_claims`
- `qa.answer_drafts`
- `qa.answer_citations`
- `qa.citation_verification_runs`
- `qa.citation_verification_items`
- `qa.final_answer_audits`

这层要解决的核心问题：

1. 多路召回各 lane 命中了什么
2. 最终答案的每个 claim 引用了什么对象
3. 审核模型是否确认 citation 真正支持该 claim
4. 是否满足 release gate，避免“看起来像引用、实际上不支持”的情况


这层是本文最重要的新增建议。

建议你后续把“数据字典”作为**一等公民**来落地，而不是散落在 term map 和脚本里。

#### `dict.term_dictionary`
术语字典。

建议字段：
- `term_id`
- `canonical_term`
- `language`
- `term_type`
- `description`
- `source`

#### `dict.alias_dictionary`
别名字典。

建议字段：
- `alias_id`
- `canonical_term_id`
- `alias`
- `alias_class`
- `language`
- `community_frequency`
- `confidence`

#### `dict.build_dictionary`
build 字典。

建议字段：
- `build_id`
- `class_name`
- `build_name`
- `build_name_zh`
- `aliases jsonb`
- `core_skills jsonb`
- `core_gear jsonb`
- `farm_targets jsonb`
- `phase`

#### `dict.rule_dictionary`
规则字典。

建议字段：
- `rule_id`
- `rule_type`
- `subject_type`
- `description`
- `rule_jsonb`

适合存：
- breakpoint 规则
- cube 规则分类
- drop 规则说明
- build route 规则模板

#### `dict.item_dictionary`
物品字典。

建议字段：
- `item_id`
- `canonical_name`
- `canonical_name_zh`
- `item_family`
- `rarity`
- `base_code`
- `normalized_keywords jsonb`

#### `dict.area_dictionary`
区域字典。

建议字段：
- `area_id`
- `canonical_name`
- `canonical_name_zh`
- `act`
- `area_tags jsonb`
- `farm_tags jsonb`

---

## 5. 当前“已落地版”与“推荐演进版”的关系

### 5.1 当前已落地版（仓库现状）

当前 `sql/postgres/001_core_schema.sql` 已经落了这些表：

- `d2.documents`
- `d2.chunks`
- `d2.search_aliases`
- `d2.build_archetypes`
- `d2.build_core_skills`
- `d2.base_items`
- `d2.runes`
- `d2.runewords`
- `d2.runeword_runes`
- `d2.runeword_item_types`
- `d2.runeword_modifiers`
- `d2.skills`
- `d2.skill_prerequisites`
- `d2.cube_recipes`
- `d2.cube_recipe_inputs`
- `d2.areas`
- `d2.unique_items`
- `d2.monster_resistances`
- `d2.monster_resistance_values`
- `d2.breakpoints`
- `d2.breakpoint_points`

### 5.2 当前版本的优点

- 已经够做 **PG 能力验证**
- 已经够支撑：
  - Enigma 配方
  - Spirit FCR 变量
  - 技能前置链
  - 区域等级
  - 怪物抗性
  - breakpoint 查表

### 5.3 当前版本的不足

- `entities / facts / edges / dict` 还没有完整拆层
- `BM25 + vector + graph expansion` 的融合还在 SQL/应用层草图阶段
- `DROPS_IN / USED_BY_BUILD / REQUIRES_BASE` 等 gameplay edges 还不够丰富
- 数据字典还没有正式作为独立 schema 落地

---

## 6. 多路召回流程设计

### 6.1 四路并行召回

#### 路 1：Alias / trigram lane
查：
- `core.aliases`
- `dict.alias_dictionary`
- `search.query_alias_rules`

用途：
- 黑话
- 错拼
- 缩写
- 社区俗称

#### 路 2：BM25 lane
查：
- `search.chunks`
- `search.chunk_fts`

用途：
- 标题命中
- FAQ 命中
- 攻略段落召回
- 机制说明文本召回

#### 路 3：Embedding lane
查：
- `search.chunk_embeddings`

用途：
- 机制问题
- 语义相似 chunk
- build 类问题

#### 路 4：Graph expansion lane
查：
- `core.edges`
- `graph.entity_neighbors_mv`
- `WITH RECURSIVE`

用途：
- `Runeword -> Rune`
- `Build -> Skill`
- `Build -> CoreGear`
- `Area -> Monster`
- `Monster -> Resistance`

---

## 6.1 Query Understanding 设计重点

为了保证召回率强、结果又准，query understanding 不能只做简单同义词替换，必须分成四步：

### 第一步：输入归一化
- 清洗空白、标点、大小写、全半角
- 抽取数值、百分比、单位、职业、技能、物品、场景
- 标注是否是：
  - fact lookup
  - numeric reasoning
  - build strategy
  - multi-hop graph

### 第二步：rewrite 候选生成
至少生成以下类型候选：
- identity rewrite
- alias normalized rewrite
- canonical term rewrite
- constrained rewrite（保留职业/难度/版本约束）
- subquestion seed rewrite

### 第三步：子问题拆解
以下场景建议强制拆 subquestions：
- 数值档位问题
- build -> 核心装备 -> 底材 -> 场景 路径问题
- 掉落/场景效率问题
- 存在多个实体歧义的问题

### 第四步：检索计划选择
不同 query type 要绑定不同 retrieval policy：
- fact lookup：alias + bm25 + graph
- numeric reasoning：alias + rule lookup + numeric table + graph
- multi-hop strategy：alias + graph + bm25 + vector

这样做的目的，是让“高 recall”与“高 precision”不是靠 prompt 一次性赌出来，而是靠结构化的 query planning 来保证。

## 6.2 结果正确性与引用严谨性

最终答案必须经过至少三层 gate：

### Gate 1：grounding gate
- 关键 claim 必须能映射到 `document/chunk/fact/edge/rule` 之一
- 不能只靠模型自由生成

### Gate 2：numeric gate
- 所有数值类结论必须来源于：
  - breakpoint 表
  - cube 规则
  - structured fact
  - 明确公式
- 禁止未经规则支持的线性插值

### Gate 3：citation verification gate
- 最终草稿答案必须记录 citation
- 再由“门口模型/审核模型”检查：
  - cited object 是否真实存在
  - cited object 是否支持 claim
  - 是否有不支持或越界引用

只有通过 gate 的答案，才应该进入最终 release。


## 7. 中文 / 中英混合场景的数据库适配建议

### 7.1 不要直接把中文全文检索寄希望于默认 parser

更稳的方案是：

1. 先在离线流程里做术语归一
2. 生成预分词字段
3. 把“中文 / 英文 / 中英混合”拆成不同 lexical lane

建议字段：
- `lexical_text_zh`
- `lexical_text_en`
- `lexical_text_mixed`

### 7.2 别名必须进字典层

不要只留在：
- `bilingual-term-map.json`
- `curated anchor`

而要正式进入：
- `dict.alias_dictionary`
- `core.aliases`

### 7.3 实体-文本桥表必须有

建议加：
- `search.chunk_entities(chunk_id, entity_id, role, confidence)`

这样 graph lane 和 text lane 才能自然融合。

---

## 8. 后续数据字典落地适配计划

本节是为你后续“数据字典”预留的正式落地说明。

### 8.1 第一批优先字典

#### A. 术语与别名字典
来源：
- `bilingual-term-map.json`
- `alias-registry.jsonl`
- curated anchors

落地到：
- `dict.term_dictionary`
- `dict.alias_dictionary`

#### B. Build 字典
来源：
- `build-archetypes.jsonl`
- 后续 guide / build 抽取

落地到：
- `dict.build_dictionary`

#### C. 规则字典
来源：
- `breakpoints.jsonl`
- `cube-recipes.jsonl`
- 公式资料

落地到：
- `dict.rule_dictionary`

#### D. 物品字典
来源：
- `base-items.jsonl`
- `unique-items.jsonl`
- `runes.jsonl`
- `runewords.jsonl`

落地到：
- `dict.item_dictionary`

#### E. 区域/怪物字典
来源：
- `areas.jsonl`
- `monster-resistances.jsonl`

落地到：
- `dict.area_dictionary`
- `dict.monster_dictionary`

### 8.2 第二批字典

- 掉落规则字典
- Build progression 字典
- Mercenary 字典
- FAQ question pattern 字典
- Query routing rule 字典

---

## 9. 推荐索引策略

### 9.1 alias / blackword
- `GIN(alias gin_trgm_ops)`

### 9.2 documents / chunks
- `GIN(search_vector)`
- `GIN(title gin_trgm_ops)`
- `GIN(normalized_text gin_trgm_ops)`
- `GIN(metadata jsonb_path_ops)`

### 9.3 embedding
- `HNSW` 优先
- `IVFFlat` 作为备选

### 9.4 graph
- `(subject_id, predicate)`
- `(object_id, predicate)`
- `ltree` GiST / GIN

### 9.5 rules/facts
- `(subject_id, predicate)`
- `(predicate, value_num)`
- `(predicate, value_text)`

---

## 10. 推荐优化路径

### Phase 1：先做稳定主链路
- alias + trigram
- BM25
- vector
- recursive graph expansion

### Phase 2：再做融合
- RRF
- source weighting
- authority weighting
- language weighting

### Phase 3：再做加速
- materialized views
- precomputed neighborhoods
- partitioning
- pgvectorscale（如果真的需要）

---

## 10.1 站点内容 -> chunk schema -> PostgreSQL 的格式化方法

后续数据更新建议统一遵循以下格式化链：

### Step 1：站点抓取 / 原始落盘
目标：把站点内容先保存到 `docs/tier0/raw/...`。

典型脚本：
- `scripts/fetch_tier0.py`
- `scripts/fetch_high_value_pages.py`
- `scripts/fetch_purediablo_high_value.py`
- `scripts/fetch_91d2_high_value.py`

### Step 2：原始内容 -> normalized documents
目标：转成统一 `documents.jsonl`。

核心字段：
- `doc_id`
- `source_id`
- `source_url`
- `title`
- `text`
- `authority_tier`
- `lane`

典型脚本：
- `scripts/normalize_tier0.py`
- `scripts/build_merged_normalized.py`

### Step 3：documents -> chunks
目标：生成统一 chunk schema。

当前 chunk 关键字段：
- `chunk_id`
- `doc_id`
- `source_id`
- `title`
- `chunk_index`
- `text`
- `char_count`

### Step 4：chunks -> PG search bundle
目标：把 merged 文本层与 structured 层打包到 PG 可导入数据。

典型脚本：
- `scripts/build_postgres_bundle.py`
- `scripts/build_pg_dict_bundle.py`

### Step 5：bundle -> PostgreSQL tables
目标：导入 PG 主表与字典/query-understanding 表。

典型脚本：
- `scripts/load_postgres_bundle.py`
- `scripts/load_pg_dict_bundle.py`

这个链条的设计目的，是让后续站点更新时不需要重写“导入逻辑”，只需要在 raw/normalized/chunks/structured 层刷新，再重建 PG bundle。

## 10.2 CLI 接口（用于后续持续更新）

新增统一 CLI：

- `scripts/d2_pg_cli.py`

### 查看可用阶段与流水线

```bash
.venv/bin/python scripts/d2_pg_cli.py show-plan
```

### 只跑某一个阶段

```bash
.venv/bin/python scripts/d2_pg_cli.py stage structured-support
```

### 从站点抓取一直到 PG 资产包

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
```

### 只刷新 PG 检索资产（适合站点更新后重建）

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-pg-search
```

### 导入 PostgreSQL 主 bundle

```bash
.venv/bin/python scripts/d2_pg_cli.py load-pg --database-url 'postgresql://user:pass@host:5432/db'
```

### 导入 PostgreSQL 字典 / query-understanding bundle

```bash
.venv/bin/python scripts/d2_pg_cli.py load-dict --database-url 'postgresql://user:pass@host:5432/db'
```

### 当前 CLI 对应的三个主要 pipeline

- `site-to-chunks`
  - 抓取 -> 规范化 -> 合并 chunk 资产
- `site-to-pg-assets`
  - 抓取 -> 规范化 -> 合并 -> structured support -> PG bundle -> dict bundle
- `refresh-pg-search`
  - 不重新抓取，只重建 PG 检索资产与 runtime verification

这正是后续“数据更新”所需要的详细能力入口。


## 11. 与当前实现对应的文件入口

### SQL / Schema
- `sql/postgres/001_core_schema.sql`
- `sql/postgres/002_optional_vector.sql`
- `sql/postgres/003_views.sql`
- `sql/postgres/queries.sql`

### Bundle / 导入
- `scripts/build_postgres_bundle.py`
- `scripts/load_postgres_bundle.py`
- `scripts/verify_postgres_bundle.py`
- `docs/tier0/postgres-bundle/`

### 数据支撑层
- `docs/tier0/structured/*.jsonl`
- `docs/tier0/alias-registry.jsonl`
- `docs/tier0/build-archetypes.jsonl`

---

## 12. 一句话结论

当前最合理的数据库设计方向不是：

> “把 PostgreSQL 强行伪装成一个只会说 Cypher 的图数据库”

而是：

> “把 PostgreSQL 设计成一个统一检索数据库：同时承载 alias、BM25、embedding、结构化事实、关系扩展和数据字典。”

这也是当前仓库后续最值得继续推进的路线。

## 13. PostgreSQL 运行时适配

当前运行时已新增：

- `app/postgres_store.py`

设计原则：

1. 优先 PostgreSQL，多路召回仍保持 alias / lexical / graph / structured support 的组合思路
2. PostgreSQL 不可用时，允许回退到当前本地 Chroma + JSONL graph，保证开发期连续性
3. 后续真正切换到 PG-only 时，只需要把 `RETRIEVAL_BACKEND=postgres` 固定化，并逐步减少本地 fallback 的职责

当前 PostgreSQL 运行时查询重点：

- `dict.searchable_aliases`
- `d2.entity_catalog`
- `d2.gameplay_edges`
- `d2.chunks`
- `dict.rule_dictionary`

因此它已经具备“从 PG 做 alias + lexical + graph term expansion”的主路径能力，只是向量 lane 仍待后续真正接入 PostgreSQL embedding 列。

## 14. PostgreSQL 向量资产包

为了让 PostgreSQL 最终承担 embedding lane，当前仓库已新增：

- `docs/tier0/postgres-embedding-bundle/`
- `scripts/build_pg_embedding_bundle.py`
- `scripts/load_pg_embedding_bundle.py`
- `scripts/verify_pg_embedding_bundle.py`

当前设计采用与本地运行时一致的 `local-hashing-v1` 向量基线，先保证：

1. chunk schema 可以稳定生成向量
2. PostgreSQL `d2.chunks.embedding` 可以被批量回填
3. 后续可以再替换为正式多语言 embedding 模型，而不需要改数据库链路

## 15. PostgreSQL BM25 运行时适配

当前运行时已在 `app/postgres_store.py` 中补入：

- `supports_bm25_runtime()`
- `_bm25_query()`

运行原则：

1. PostgreSQL 安装了 `pg_textsearch` 且建立了 BM25 索引时，优先尝试 `postgres_bm25` lane。
2. 如果 BM25 扩展不可用，则回退到 PostgreSQL lexical/trigram lane。
3. 最后仍可回退到本地检索基线，确保开发期连续性。

这使得 PostgreSQL 主路径已经开始覆盖：

- alias lane
- lexical/trigram lane
- BM25 lane（条件开启）
- vector lane（条件开启）
- grounding lane（已接 canonical claims / provenance）


补充：当前应用端在 PostgreSQL 运行时里会根据实际参与的 lane，把 `actual_backend` 区分为 `postgres-lexical` / `postgres-bm25` / `postgres-vector` / `postgres-hybrid`。


补充：当前 PostgreSQL 主 bundle 已纳入 `curated anchor` 层，最新实测计数为 `documents=511`、`chunks=8708`、`chunks_with_embedding=8708`。`超市`、`乔丹` 等 query 已能在 PG 主路径下把 curated anchor 顶到前列。


最新 fresh evidence（2026-04-23，本机实测）：

- `劳模掉不掉军帽？` -> `postgres-hybrid`，Top1 = `Mephisto / 劳模（Curated Anchor Card）`
- `超市是什么？` -> `postgres-hybrid`，Top1 = `Chaos Sanctuary / 超市（Curated Anchor Card）`
- `乔丹是什么？` -> `postgres-hybrid`，Top1 = `Stone of Jordan / 乔丹（Curated Anchor Card）`
- `我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？` -> `postgres-hybrid`，Top1 = `Spirit Shield / 精神盾（Curated Anchor Card）`

说明当前 PostgreSQL 主路径的加权融合，已经能把 curated anchor 在关键 query type 下稳定推到前列。


补充：当前仓库已新增 `sql/postgres/007_strategy_views.sql`，用于把 build -> runeword -> base -> farm area 这类启发式 support 固化成 PostgreSQL 可查询的 strategy edges。


补充：当前仓库已新增 `docs/tier0/postgres-strategy-bundle/` 与 `scripts/build_pg_strategy_bundle.py`，用于把 `d2.strategy_edges` 导出成可版本化、可导入、可校验的正式资产。


补充：当前 `strategy bundle` 不再只是导出文件，已对应到 PostgreSQL 持久表 `d2.strategy_edge_facts`，运行时 graph expansion 会优先消费它。


补充：当前应用返回已新增 `ranking_reasons`，用于解释为什么某个 chunk/结构化证据排在前面，包括 lane 原因与 strategy reason。


补充：当前应用返回已新增 `reason_summary`，用于把 `ranking_reasons` 压缩成可直接供回答阶段消费的解释摘要。


补充：当前仓库已新增 `scripts/verify_api_pg_runtime.py`，用于在 HTTP 层验证 `/health`、`/qa`、`ranking_reasons`、`reason_summary` 与 PostgreSQL-backed runtime。


补充：当前仓库已新增 `scripts/verify_llm_reasoned_answers.py`，用于验证 `use_llm=true` 时最终回答能够消费 `reason_summary` 与 `ranking_reasons`。

## 16. 问答链路的 `qu / qa` 实际落地建议

为了让“输入 -> 召回 -> 回答 -> 校验”是可审计的，建议把 `dict / qu / qa` 三层区分清楚：

### `dict`

负责“静态知识字典”：

- alias / canonical / item / build / area / monster / rule

### `qu`

负责“单次 query understanding 过程”：

- 原始 query
- rewrite
- entity resolution candidates
- subquestion plan
- retrieval plan lanes
- answer constraints

### `qa`

负责“单次 answer release 过程”：

- retrieval run
- lane hits
- evidence claims
- answer draft
- answer citations
- citation verification
- final answer audit

这种拆法的意义是：

1. 字典可以持续迭代
2. query understanding 可以复盘
3. answer gate 可以审计

## 17. Prompt Rewrite / Query Understanding 的 schema 约束

为了保证召回率强、同时结果要准，建议坚持以下约束：

1. **identity rewrite 永远保留**
2. alias rewrite 与 canonical rewrite 分开记
3. 约束词（constraint term）要单独入 `qu.query_rewrite_terms`
4. 子问题计划必须和主 rewrite 绑定
5. retrieval policy 与 answer constraints 必须表驱动

当前仓库已基本按这个思路实现：

- `dict.query_pattern_dictionary`
- `qu.query_rewrites`
- `qu.query_rewrite_terms`
- `qu.subquestion_plans`
- `qu.subquestion_steps`
- `qu.retrieval_policies`
- `qu.answer_constraints`

## 18. 数据格式化规范

建议把“站点内容 -> 可检索资产”明确分成四类：

1. **document**
2. **chunk**
3. **structured support**
4. **strategy facts**

推荐原则：

- narrative 文本进入 `documents/chunks`
- 高风险表格进入 `structured support`
- build -> runeword -> base -> area 进入 `strategy facts`
- alias / 黑话 / 错拼进入 `dict bundle`

## 19. 可扩展的数据更新策略

后续数据更新，不要直接改 PG 表；优先走：

```text
source update
  -> normalized assets
  -> postgres bundles
  -> verify bundles
  -> load bundles
  -> full stack verify
```

推荐命令：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
.venv/bin/python scripts/d2_pg_cli.py load-pg --database-url "$DATABASE_URL"
.venv/bin/python scripts/d2_pg_cli.py load-dict --database-url "$DATABASE_URL"
.venv/bin/python scripts/d2_pg_cli.py load-embeddings --database-url "$DATABASE_URL"
.venv/bin/python scripts/d2_pg_cli.py load-strategy --database-url "$DATABASE_URL"
.venv/bin/python scripts/d2_pg_cli.py stage full-stack-verify
```

## 20. 当前数据库设计的一句话结论

当前最值得坚持的方向是：

> PostgreSQL 不是只做“存 chunk 的向量库”，而是同时承担 dict / qu / qa / multi-lane retrieval / release gate 的统一检索数据库。
