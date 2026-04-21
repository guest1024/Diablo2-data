# 中英文混合 GraphRAG 技术方案（面向本项目）

这份文档是在当前项目已有数据基础上，对“中英文混合 GraphRAG”做的**可落地版本**方案。  
目标不是抽象讨论，而是让你后续开发时可以直接按步骤实现。

---

## 1. 结论先行

你的原始方案 **可行**，但需要结合当前项目状态做 4 个关键收敛：

1. **主入口固定为 `docs/tier0/merged/`**
2. **Chunk 结构必须统一成一个最终 schema**
3. **检索采用 alias + lexical + vector + graph 四路混合**
4. **图谱和文本分工明确：图做定位与约束，文本做证据与生成**

---

## 2. 当前项目基础

当前项目已经有：

- 基础主语料
- 高价值详情页语料
- PureDiablo 中文/英文补充层
- `merged` 主知识层
- canonical entities / canonical claims / provenance
- export bundle / csv / quickstart / handoff / query recipes

主入口：

- `docs/tier0/merged/`

主文件：

- `normalized/documents.jsonl`
- `chunks.jsonl`
- `canonical-entities.jsonl`
- `canonical-claims.jsonl`
- `provenance.jsonl`
- `export-bundle.json`

---

## 3. 对你原方案的调整意见

## 3.1 可保留的核心设计

下面这些方向是正确的：

- 多语言向量空间
- 混合检索（语义 + 关键词 + 图）
- 统一重排序
- 图谱增强
- FAQ / PDF / 文章 / JSON 统一抽象

## 3.2 需要修正的地方

### A. 不建议把 embedding 直接放进 Chunk 主对象

你写的：

```json
{
  "id": "...",
  "content": "...",
  "embedding": [...]
}
```

更推荐：

- chunk 主数据不内嵌 embedding
- embedding 单独存索引层

原因：

- 后续你可能切换 embedding 模型
- 同一 chunk 可能有多套 embedding（entity / evidence）
- 内嵌会让 JSONL 过大、更新昂贵

### B. `doc_type` 不够，需要补 `authority_tier / game_variant / version_tokens`

因为 Diablo II 问答里最容易错的不是“文档类型”，而是：

- 来源权威性
- LoD / D2R 混答
- 补丁差异

### C. 图谱结果不要只文本化后参与排序

图谱不只是 text expansion 的来源，它还应该承担：

- entity disambiguation
- source constraint
- version constraint
- contradiction visibility

---

## 4. 推荐的最终数据模型

## 4.1 原文层

保存原始抓取：

```text
raw/
```

字段关注：

- source_url
- local_path
- source_id
- fetched_at

---

## 4.2 文档层（normalized documents）

```json
{
  "doc_id": "...",
  "source_id": "...",
  "source_url": "...",
  "local_path": "...",
  "title": "...",
  "text": "...",
  "char_count": 12345,
  "language": "zh|en|mixed",
  "doc_type": "wiki|faq|guide|manual|forum|reference",
  "authority_tier": "official|structured_db|wiki|guide|forum",
  "game_variant": "classic|lod|d2r|unknown",
  "version_tokens": ["1.13", "2.4"]
}
```

---

## 4.3 Chunk 层（推荐最终统一 schema）

推荐统一成：

```json
{
  "chunk_id": "...",
  "doc_id": "...",
  "source_id": "...",
  "source_url": "...",
  "title": "...",
  "text": "...",
  "chunk_index": 1,
  "char_count": 800,
  "language": "zh|en|mixed",
  "chunk_type": "entity|guide_section|faq|table_text|relation_summary|manual_section",
  "authority_tier": "official|structured_db|wiki|guide|forum",
  "game_variant": "classic|lod|d2r|unknown",
  "version_tokens": ["1.13", "d2r-unspecified"],
  "entity_ids": ["Runeword:spirit", "Rune:tal"],
  "keywords": ["Spirit", "精神", "符文之语"]
}
```

### 说明
- `entity_ids`：必须有，哪怕暂时为空数组
- `keywords`：给 BM25/关键词检索用
- `chunk_type`：帮助检索和重排序

---

## 4.4 图谱层

### 节点
- `canonical-entities.jsonl`

### Claims
- `canonical-claims.jsonl`

### Provenance
- `provenance.jsonl`

### 辅助
- `aliases.jsonl`
- `version-tags.jsonl`
- `contradiction-seeds.jsonl`

---

## 5. Chunk 处理策略（落地版）

## 5.1 Wiki / 资料页

按知识对象切：

- summary
- stats
- requirements
- notes
- drops / source
- version differences

## 5.2 FAQ

一问一答一个 chunk：

```text
问题：...
答案：...
```

## 5.3 攻略 / Build

按结构切：

- build summary
- skill plan
- gear
- merc
- route
- FAQ

## 5.4 PDF / Manual

按标题层级切：

- chapter
- subchapter
- large paragraph recursive split

## 5.5 表格

不要原样保留成不可读表。

转成描述性文本，例如：

```text
Item: Spirit
Required runes: Tal, Thul, Ort, Amn
Allowed bases: Sword, Shield
```

---

## 6. 检索架构（推荐）

## 6.1 四路召回

### 路 1：Alias / exact match
用途：
- 实体定位
- 中英术语打通

### 路 2：BM25 / lexical
用途：
- 精确术语
- 技能名 / 符文名 / 地图名 / build 名

### 路 3：Dense vector
用途：
- 语义召回
- 长问题
- FAQ / build / 机制解释

### 路 4：Graph expansion
用途：
- 关系补全
- 多跳信息
- 版本/来源约束

---

## 6.2 推荐检索顺序

1. query 语言识别
2. alias expansion
3. canonical entity lookup
4. lexical + dense parallel recall
5. graph neighborhood expansion
6. 合并候选
7. rerank
8. 证据裁剪
9. LLM 生成

---

## 7. Embedding 方案（推荐）

## 7.1 模型选择

当前更适合你的路线：

- embedding：`BGE-M3`
- reranker：`bge-reranker-v2-m3`

原因：
- 多语言
- 支持长文本
- 兼顾 dense / sparse / multi-vector 能力  
参考：
- BGE-M3 model card: https://huggingface.co/Enno-Ai/bge-m3
- BGE reranker v2 m3: https://huggingface.co/BAAI/bge-reranker-v2-m3

## 7.2 两类 embedding

### A. entity embedding
输入：
- canonical name
- aliases
- node_type
- short summary

### B. evidence embedding
输入：
- chunk text
- source
- authority
- game_variant
- version_tokens

不要混成一套。

---

## 8. 关键词检索（BM25）建议

## 8.1 中文
- `jieba`

## 8.2 英文
- 标准 tokenizer

## 8.3 索引字段
- `text`
- `title`
- `keywords`
- `aliases`

注意：
- 中文分词准确性对召回影响非常大
- 术语表和 alias 要先补齐

---

## 9. 向量数据库与图数据库选型

## 9.1 向量库

### 开发
- `Chroma`

### 生产
- `Qdrant`

原因：
- Qdrant 原生适合 hybrid 检索、dense+sparse 组合  
参考：
- Qdrant hybrid reranking: https://qdrant.tech/documentation/advanced-tutorials/reranking-hybrid-search/

## 9.2 图数据库
- `Neo4j`

原因：
- 生态成熟
- 适合 property graph
- 对 GraphRAG 资料和实践丰富  
参考：
- Neo4j GraphRAG user guide: https://neo4j.com/docs/neo4j-graphrag-python/current/user_guide_rag.html
- Neo4j GraphRAG overview: https://neo4j.com/labs/genai-ecosystem/graphrag/

---

## 10. 重排序策略

## 10.1 推荐

统一候选后，用一个 multilingual reranker 做公平打分。

输入：
- query
- candidate chunk text

输出：
- relevance score

## 10.2 排序要额外叠加的业务因子

不仅看 reranker 分数，还要叠加：

- authority_tier
- language fit
- game_variant fit
- version fit
- supporting_source_count

即：

```text
final_score = reranker_score
            + authority_bonus
            + version_bonus
            + language_bonus
            + support_bonus
```

---

## 11. GraphRAG 增强建议

## 11.1 图里最值得先保的节点

- Runeword
- UniqueItem
- SetItem
- BaseItem
- Rune
- Recipe
- Skill
- Class
- Monster
- Area
- Quest
- NPC
- Patch
- SourceDocument

## 11.2 最值得先保的边

- `ALIASES`
- `DESCRIBES`
- `BELONGS_TO_SOURCE`
- `SUPPORTS_ENTITY`
- `USES_RUNE`
- `REQUIRES_BASE`
- `DROPS_IN`
- `USED_BY_BUILD`
- `BELONGS_TO_CLASS`
- `EVIDENCED_BY`
- `OVERRIDES_IN_PATCH`
- `CONTRADICTS`

---

## 12. 中英文混合问答流程（推荐）

1. 检测 query 语言
2. alias expansion（中英双向）
3. canonical entity 定位
4. graph 扩展
5. canonical claims 检索
6. provenance 过滤
7. chunk 召回
8. authority/version rerank
9. 生成答案
10. 输出来源与版本说明

---

## 13. 当前方案的可行性评价

### 你的原方案可行的部分
- 混合检索
- 多语言 embedding
- 统一重排序
- GraphRAG 增强
- 分类型 chunk

### 需要补强的地方
1. 先把 canonical / alias / provenance 做扎实
2. 不要把 embedding 直接塞进主 chunk schema
3. Graph 不只是扩展文本，还要承担版本/来源/冲突约束
4. merged 主层必须作为生产入口

---

## 14. 你后续最推荐的实施顺序

### 第一步
把 `merged/` 作为主库固定下来

### 第二步
做 alias + canonical 检索链路

### 第三步
做 entity embedding + evidence embedding

### 第四步
做 BM25 + dense + graph hybrid 检索

### 第五步
接 Neo4j / Qdrant

### 第六步
做中英文评测集

### 第七步
继续补中文高质量数据

---

## 15. 一句话建议

> 先把 **canonical entity / alias / provenance / version** 做对，再调 embedding；先把 **merged 主层** 做稳，再谈复杂 GraphRAG 技巧。

