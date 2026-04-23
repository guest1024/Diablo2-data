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
