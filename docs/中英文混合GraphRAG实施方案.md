# 中英文混合 GraphRAG 实施方案（执行版）

这份文档面向**真正开始开发**的阶段。  
目标不是讨论概念，而是把当前项目已有的数据底座，推进成一个可运行的中英文混合 GraphRAG 问答系统。

当前约束与前提：

- 主知识层：`docs/tier0/merged/`
- 数据规范：`docs/data-spec-v1.md`
- 技术路线说明：`docs/中英文混合GraphRAG技术方案.md`
- 向量数据库：**ChromaDB**
- 图数据库：**Neo4j**

---

## 1. 最终目标

构建一套能够回答以下问题的系统：

1. 中文 / 英文 / 中英混合问句
2. 装备 / 符文之语 / 技能 / 怪物 / 地图 / 任务
3. FAQ / build / 开荒 / MF / 经验类问题
4. 版本相关问题（LoD / D2R）
5. 带来源证据的问答

输出要求：

- 有结论
- 有证据
- 有来源
- 有版本说明（如果相关）
- 有中英文术语映射（如果相关）

---

## 2. 当前直接可用的数据入口

## 2.1 主问答入口（必须固定）

后续系统开发只以以下文件作为主入口：

### 文本检索
- `docs/tier0/merged/normalized/documents.jsonl`
- `docs/tier0/merged/chunks.jsonl`

### 图谱检索
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`
- `docs/tier0/merged/relation-taxonomy.json`

### 图层导出
- `docs/tier0/merged/export-bundle.json`
- `docs/tier0/merged/csv/manifest.json`

### 辅助能力
- `docs/tier0/merged/sample-queries.json`
- `docs/tier0/query-recipes.md`
- `docs/tier0/bilingual-graphrag-guidelines.md`

### Chroma 导入包
- `docs/chroma-ready/documents.jsonl`
- `docs/chroma-ready/chunks.jsonl`
- `docs/chroma-ready/manifest.json`

---

## 3. 系统拆分

推荐拆成 6 个模块：

1. `ingestion`
2. `entity-resolution`
3. `retrieval`
4. `graph-expansion`
5. `rerank`
6. `answering`

---

## 4. 模块设计

## 4.1 ingestion（数据导入）

### 目标
把当前 JSONL / CSV / graph bundle 导入到运行时系统。

### 输入
- merged documents / chunks
- canonical entities / claims / provenance
- relation taxonomy
- Chroma-ready 包

### 输出
- Chroma collections
- Neo4j nodes / edges / claims / provenance
- 本地 alias index

### 要做的事
1. 读取 `docs/chroma-ready/chunks.jsonl`
2. 读取 `docs/chroma-ready/documents.jsonl`
3. 导入 ChromaDB
4. 读取 `docs/tier0/merged/csv/`
5. 导入 Neo4j
6. 本地缓存 alias 表

---

## 4.2 entity-resolution（实体解析）

### 目标
把用户问题里的术语映射到 canonical entity。

### 输入
- query
- `merged/aliases.jsonl`
- `merged/canonical-entities.jsonl`

### 输出
- `candidate_entities`

### 规则
1. 先做 query normalization
2. 做 alias exact match
3. 做 alias fuzzy match
4. 如果还不够，再做 entity embedding 检索

### 产出格式建议

```json
{
  "query": "精神盾底材是什么",
  "language": "zh",
  "resolved_entities": [
    {
      "canonical_id": "Runeword:spirit",
      "score": 0.97,
      "match_type": "alias_exact"
    }
  ]
}
```

---

## 4.3 retrieval（文本检索）

### 目标
从 chunk 层召回证据文本。

### 检索路线

并行四路：

1. alias / exact
2. lexical / BM25
3. dense embedding
4. graph neighborhood text expansion

### 输入
- query
- resolved entities
- `merged/chunks.jsonl`

### 输出
- `candidate_chunks`

### 推荐实现

#### A. Chroma collection
- `evidence_chunks`
  - 文档：chunk text
  - metadata：
    - `doc_id`
    - `source_id`
    - `language`
    - `authority_tier`
    - `game_variant`
    - `version_tokens`
    - `chunk_type`
    - `entity_ids`

#### B. 关键词检索
- 中文：`jieba`
- 英文：标准 tokenizer
- 字段：
  - title
  - text
  - keywords
  - aliases

---

## 4.4 graph-expansion（图扩展）

### 目标
利用图谱做结构化扩展，而不只是文本召回。

### 输入
- resolved entities
- Neo4j graph

### 输出
- graph-derived candidates

### 优先关系
- `ALIASES`
- `DESCRIBES`
- `BELONGS_TO_SOURCE`
- `SUPPORTS_ENTITY`
- 后续再补：
  - `USES_RUNE`
  - `REQUIRES_BASE`
  - `DROPS_IN`
  - `USED_BY_BUILD`
  - `OVERRIDES_IN_PATCH`
  - `CONTRADICTS`

### 推荐扩展深度
- 默认 1~2 hop
- 复杂机制问题最多 3 hop

---

## 4.5 rerank（统一重排）

### 目标
把图结果和文本结果放到同一排序框架里。

### 输入
- query
- chunk candidates
- graph candidates

### 输出
- top-k context

### 排序因子

最终分数建议：

```text
final_score =
  reranker_score
  + authority_bonus
  + language_bonus
  + version_bonus
  + support_bonus
```

### 必须考虑的字段
- `authority_tier`
- `language`
- `game_variant`
- `version_tokens`
- `supporting_source_count`

---

## 4.6 answering（答案生成）

### 目标
输出一个可用、可解释、可溯源的答案。

### 输入
- top-k chunks
- graph facts
- provenance

### 输出结构建议

```json
{
  "answer": "...",
  "entities": ["Runeword:spirit"],
  "version_scope": ["d2r"],
  "sources": [
    {
      "source_id": "diablo2-io",
      "evidence_url": "...",
      "authority_tier": "structured_db"
    }
  ],
  "evidence_chunks": ["chunk_id_1", "chunk_id_2"]
}
```

### 答案模板建议
- 结论
- 适用版本
- 核心属性 / 说明
- 证据来源
- 若有冲突则列出

---

## 5. ChromaDB 具体用法

## 5.1 推荐 collections

### collection 1：`entity_cards`
用于实体定位

输入：
- canonical name
- aliases
- node_type
- short summary

### collection 2：`evidence_chunks`
用于证据检索

输入：
- chunk text
- metadata

### collection 3（可选）：`faq_chunks`
用于 FAQ / build / 经验类问题

---

## 5.2 导入接口

每条数据结构固定：

```json
{
  "id": "...",
  "content": "...",
  "metadata": { ... }
}
```

导入方式：

```python
collection.add(
    ids=[...],
    documents=[...],
    metadatas=[...]
)
```

不要把 embedding 存回主 JSONL 文件。

---

## 6. Neo4j 具体用法

## 6.1 第一批导入
- nodes
- edges
- claims
- provenance

## 6.2 最小 Cypher 能力
1. alias -> entity
2. entity -> claim
3. claim -> provenance
4. entity -> neighbor

## 6.3 当前最适合用法
- 图谱负责：
  - 定位
  - 关系扩展
  - 版本/来源约束
- 文本负责：
  - 证据正文
  - 生成上下文

---

## 7. 中英文混合检索的执行细则

## 7.1 语言识别
先识别：
- zh
- en
- mixed

## 7.2 query expansion
做：
- alias expansion
- 中英同义映射
- 常见缩写映射

## 7.3 版本约束
如果 query 明确提到：
- D2R
- LoD
- 1.13
- Classic

必须把 `version_tokens` / `game_variant` 作为强过滤或强排序信号。

## 7.4 来源约束
若回答为强事实型：
- 官方 / structured_db 优先

若回答为 build / 经验型：
- guide / forum 可以参与，但必须保留 provenance

---

## 8. 评测方案

## 8.1 最少评测集
- 中文 50 条
- 英文 50 条
- 混合 20 条

## 8.2 分类
- 装备
- 符文之语
- 技能
- 怪物 / 地图
- 任务
- build / MF / FAQ
- 版本差异

## 8.3 指标
- alias hit rate
- entity hit rate
- chunk recall@k
- claim grounding correctness
- answer correctness

---

## 9. 开发顺序（最推荐）

### 第一步
做最小问答原型

### 第二步
把 alias lookup 做扎实

### 第三步
接 Chroma evidence retrieval

### 第四步
接 Neo4j graph expansion

### 第五步
做 rerank

### 第六步
做版本约束

### 第七步
做评测与调优

---

## 10. 当前最推荐的最小实现

如果你想最快开始开发：

1. 用 `merged/aliases + canonical-entities` 做实体解析
2. 用 `docs/chroma-ready/chunks.jsonl` 导入 Chroma
3. 用 `merged/canonical-claims + provenance` 做 grounding
4. 用 `merged/export-bundle + csv` 接 Neo4j
5. 先做一条最小问答链：
   - alias
   - chunk retrieval
   - claim grounding
   - answer generation

---

## 11. 一句话建议

> 先把 **merged 主层 + Chroma evidence retrieval + alias/canonical 解析** 做成可跑通原型，再逐步加 GraphRAG 深度和版本治理。  

