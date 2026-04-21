# Diablo II Graph Schema v1

这份文档定义当前仓库推荐的图谱分层和最小落地 schema。

---

## 1. 设计目标

当前图谱不是为了追求复杂推理，而是为了：

1. 实体定位
2. 别名归一
3. 来源追溯
4. 版本过滤
5. 检索增强

---

## 2. 图谱分层

### Layer A: Alias / Term Graph

节点：

- `AliasTerm`
- `CanonicalTerm`

边：

- `ALIAS_OF`
- `SAME_AS_TERM`
- `ABBREVIATES`
- `COMMUNITY_REFERS_TO`

对应文件：

- `docs/tier0/alias-registry.jsonl`
- `docs/tier0/term-equivalence.jsonl`

### Layer B: Entity Graph

节点：

- `Runeword`
- `UniqueItem`
- `SetItem`
- `BaseItem`
- `Rune`
- `Recipe`
- `Skill`
- `Class`
- `Monster`
- `Boss`
- `Area`
- `Quest`
- `NPC`
- `BuildArchetype`

边：

- `USES_RUNE`
- `REQUIRES_BASE`
- `DROPS_IN`
- `FOUND_IN`
- `BELONGS_TO_CLASS`
- `USES_SKILL`
- `USES_ITEM`
- `COMMONLY_USED_BY`
- `POPULAR_FOR`

对应文件：

- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/build-archetypes.jsonl`

### Layer C: Evidence / Provenance Graph

节点：

- `SourceDocument`
- `Chunk`
- `Claim`
- `Patch`

边：

- `SUPPORTED_BY`
- `EVIDENCED_BY`
- `VALID_IN_PATCH`
- `CHANGED_IN_PATCH`
- `CONTRADICTS`

对应文件：

- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`
- `docs/tier0/merged/chunks.jsonl`

---

## 3. 最小节点字段建议

### AliasTerm

```json
{
  "alias_id": "string",
  "canonical_id": "string",
  "alias": "string",
  "alias_type": "string",
  "language": "zh|en|mixed",
  "confidence": 0.95
}
```

### BuildArchetype

```json
{
  "build_id": "string",
  "canonical_name": "string",
  "class": "string",
  "core_skills": ["string"],
  "aliases": ["string"]
}
```

### Evidence / Claim

沿用当前 merged 层：

- `canonical-entities.jsonl`
- `canonical-claims.jsonl`
- `provenance.jsonl`

---

## 4. 当前推荐落地顺序

1. `alias-registry.jsonl`
2. `term-equivalence.jsonl`
3. `build-archetypes.jsonl`
4. graph 导入（Neo4j / property graph）
5. query -> alias -> entity -> evidence 的 GraphRAG 查询链

---

## 5. 当前仓库对应资产

- `docs/tier0/bilingual-term-map.json`
- `docs/tier0/curated/`
- `docs/tier0/alias-registry.jsonl`
- `docs/tier0/term-equivalence.jsonl`
- `docs/tier0/build-archetypes.jsonl`
- `docs/tier0/merged/`

---

## 6. 使用原则

### 不要做的事

- 不要把中文标题当主键
- 不要把所有 chunk 都直接升格成 Entity
- 不要忽略版本和来源

### 推荐做的事

- 先 canonicalize，再 retrieval
- 先 alias graph，再 entity graph
- 图谱服务检索，不和文本证据层混淆
