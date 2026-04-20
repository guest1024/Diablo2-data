# Diablo II GraphRAG 数据规范 v1

这份文档用于把当前项目的数据规范**钉死**，后续抓取、清洗、切片、embedding、图谱构建都以这份规范为准。

---

## 1. 规范目标

统一以下 5 类最终数据：

1. `documents`
2. `chunks`
3. `canonical_entities`
4. `canonical_claims`
5. `provenance`

附加支持数据：

- `aliases`
- `relation_taxonomy`
- `version_tags`
- `contradiction_seeds`
- `export_bundle`

---

## 2. 总体原则

### 2.1 主键语言无关
- 不允许用中文名或英文名直接做主键
- 统一使用 `canonical_id`

### 2.2 原文与规范分层
- `raw` 保原文
- `normalized` 保结构化正文
- `derived` 保 chunks / graph / claims / provenance

### 2.3 不抹平冲突
- 不同来源、不同版本的冲突知识不能硬合并
- 只能通过 `canonical_claims + provenance + version_tags + contradiction_seeds` 处理

### 2.4 中英文分开存，检索时联通
- 存储层保留 `language`
- 检索层通过 `aliases + canonical_id` 打通

### 2.5 merged 为生产主入口
后续生产问答优先使用：
- `docs/tier0/merged/`

---

## 3. 目录规范

### 3.1 最终主目录

```text
docs/tier0/merged/
  normalized/
    documents.jsonl
  chunks.jsonl
  aliases.jsonl
  provenance.jsonl
  canonical-entities.jsonl
  canonical-claims.jsonl
  support-edges.jsonl
  claim-index.jsonl
  relation-taxonomy.json
  export-bundle.json
```

### 3.2 辅助目录

```text
docs/tier0/
  high-value/
  purediablo-high-value/
  derived/
  export/
```

---

## 4. documents 规范

文件：
- `normalized/documents.jsonl`

每行一条 document。

### 必填字段

```json
{
  "doc_id": "string",
  "source_id": "string",
  "source_url": "string",
  "local_path": "string",
  "title": "string",
  "text": "string",
  "char_count": 12345
}
```

### 字段说明
- `doc_id`：文档唯一 ID，稳定生成
- `source_id`：来源站点，如 `diablo2-io` / `arreat-summit`
- `source_url`：原始 URL
- `local_path`：本地 raw 文件路径
- `title`：页面标题
- `text`：清洗后的正文
- `char_count`：正文字符数

### 约束
- `text` 不允许为空
- `char_count` 必须等于 `len(text)`
- `doc_id` 全库唯一

---

## 5. chunks 规范

文件：
- `chunks.jsonl`

每行一条 chunk。

### 必填字段

```json
{
  "chunk_id": "string",
  "doc_id": "string",
  "source_id": "string",
  "source_url": "string",
  "title": "string",
  "chunk_index": 1,
  "char_count": 1000,
  "text": "string"
}
```

### 约束
- `chunk_id` 全库唯一
- `doc_id` 必须能关联到 `documents`
- `char_count > 0`
- `text` 不允许为空

### 切片规则
- 不是按固定 token 粗切
- 先按语义段/知识对象切
- 单块建议 `500~1200` 字符级别

---

## 6. canonical_entities 规范

文件：
- `canonical-entities.jsonl`

每行一条 canonical entity。

### 必填字段

```json
{
  "canonical_id": "string",
  "node_type": "string",
  "key": "string",
  "name": "string",
  "aliases": ["string"],
  "document_count": 1,
  "supporting_source_count": 1,
  "supporting_sources": ["string"],
  "claim_count": 1
}
```

### 约束
- `canonical_id` 全局唯一
- `node_type` 必填
- `aliases` 至少包含一个值

### 推荐 node_type
- `Runeword`
- `UniqueItem`
- `SetItem`
- `BaseItem`
- `Rune`
- `Recipe`
- `Skill`
- `Class`
- `Monster`
- `Area`
- `Quest`
- `NPC`
- `SourceDocument`

---

## 7. aliases 规范

文件：
- `aliases.jsonl`

### 必填字段

```json
{
  "alias_id": "string",
  "canonical_id": "string",
  "alias": "string",
  "alias_type": "title|key|slug",
  "node_type": "string"
}
```

### 规则
- 所有 alias 必须指向一个现有 `canonical_id`
- alias 用于：
  - 中文名
  - 英文名
  - 缩写
  - 社区俗称
  - 版本旧名

---

## 8. provenance 规范

文件：
- `provenance.jsonl`

### 必填字段

```json
{
  "provenance_id": "string",
  "claim_id": "string",
  "subject_id": "string",
  "predicate": "string",
  "source_id": "string",
  "evidence_doc_id": "string",
  "evidence_url": "string",
  "authority_tier": "string",
  "lane": "string"
}
```

### 约束
- `claim_id` 必须存在
- `evidence_doc_id` 必须能关联到 `documents`
- `evidence_url` 不允许为空

### authority_tier 建议值
- `official`
- `structured_db`
- `wiki`
- `guide`
- `forum`

---

## 9. canonical_claims 规范

文件：
- `canonical-claims.jsonl`

### 必填字段

```json
{
  "canonical_claim_id": "string",
  "subject_id": "string",
  "subject_type": "string",
  "subject_name": "string",
  "subject_aliases": ["string"],
  "predicate": "string",
  "predicate_family": "string",
  "object": "string",
  "supporting_sources": ["string"],
  "supporting_source_count": 1,
  "claim_variant_count": 1
}
```

### predicate_family 目前固定
- `provenance`
- `classification`
- `availability`
- `other`

### 约束
- `subject_id` 必须指向现有 canonical entity
- `supporting_source_count >= 1`
- `supporting_sources` 不允许为空

---

## 10. version_tags 规范

文件：
- `version-tags.jsonl`

### 必填字段

```json
{
  "version_tag_id": "string",
  "doc_id": "string",
  "source_id": "string",
  "source_url": "string",
  "variant": "classic|lod|d2r|unknown",
  "version_tokens": ["string"]
}
```

### 规则
- 每个 doc 至少一条 version row
- `variant` 必须存在
- `version_tokens` 可以为空数组，但字段必须存在

---

## 11. contradiction_seeds 规范

文件：
- `contradiction-seeds.jsonl`

### 必填字段

```json
{
  "contradiction_seed_id": "string",
  "canonical_claim_id": "string",
  "subject_id": "string",
  "predicate": "string",
  "object": "string",
  "supporting_sources": ["string"],
  "observed_variants": ["string"],
  "needs_review": false
}
```

### 规则
- 这是冲突治理的占位层
- 不代表真正冲突已解决

---

## 12. export_bundle 规范

文件：
- `export-bundle.json`

### 必填结构

```json
{
  "bundle_name": "string",
  "paths": {},
  "counts": {},
  "recommended_load_order": [],
  "recommended_query_entrypoints": {}
}
```

### 规则
- `counts` 必须与真实文件行数一致
- `paths` 必须全部存在

---

## 13. merged 主入口规范

以后默认主入口固定为：

- `docs/tier0/merged/normalized/documents.jsonl`
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`
- `docs/tier0/merged/export-bundle.json`

如果新增来源，只允许：
1. 落 raw
2. 生成 normalized docs
3. 并入 merged nodes/edges/claims/chunks
4. 重建 aliases/provenance/canonical entities/canonical claims
5. 重建 export bundle / csv / docs / stats

---

## 14. embedding 规范

建议固定两类 embedding：

### entity embedding
输入：
- canonical name
- aliases
- node_type
- short summary

### evidence embedding
输入：
- chunk 正文
- source
- authority
- language
- variant/version

### 禁忌
- 不要把所有文本混成一套 embedding

---

## 15. 检索规范

推荐检索顺序固定为：

1. alias expansion
2. canonical entity lookup
3. graph neighborhood expansion
4. canonical claims filtering
5. provenance grounding
6. chunk retrieval
7. rerank by authority + language + version

---

## 16. 版本 v1 的冻结结论

从现在开始，后续新增数据和后续脚本如果要修改：

- `canonical_id`
- `subject_id`
- `claim_id`
- `provenance_id`
- `bundle paths/counts`

都必须保持向后兼容。

如果未来要改字段或主结构，必须升版本：

- `data-spec-v2.md`

