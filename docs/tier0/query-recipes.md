# Tier 0 Query Recipes

This file provides concrete query patterns for the current Tier 0 bundle.

## Neo4j Cypher recipes

### 1. Resolve an alias to a canonical entity

```cypher
MATCH (a:Alias {alias: $alias})-[:ALIASES]->(e:Entity)
RETURN e.canonical_id, e.name, e.node_type, e.aliases;
```

### 2. Get canonical claims for an entity

```cypher
MATCH (e:Entity {canonical_id: $canonical_id})-[:HAS_CLAIM]->(c:Claim)
RETURN c.predicate, c.predicate_family, c.object, c.supporting_source_count
ORDER BY c.supporting_source_count DESC, c.predicate;
```

### 3. Show provenance for a claim

```cypher
MATCH (e:Entity {canonical_id: $canonical_id})-[:HAS_CLAIM]->(c:Claim)
MATCH (p:Provenance {claim_id: c.canonical_claim_id})
RETURN c.predicate, c.object, p.source_id, p.evidence_url, p.authority_tier;
```

### 4. Find API-gated knowledge

```cypher
MATCH (e:Entity)-[:HAS_CLAIM]->(c:Claim)
WHERE c.predicate = 'api_requires_key'
RETURN e.name, e.node_type, c.object;
```

### 5. Retrieve chunks for grounded answering

```cypher
MATCH (e:Entity {canonical_id: $canonical_id})-[:HAS_CLAIM]->(c:Claim)
MATCH (p:Provenance {claim_id: c.canonical_claim_id})
MATCH (ch:Chunk {doc_id: p.evidence_doc_id})
RETURN ch.chunk_id, ch.title, ch.text
LIMIT 20;
```

## JSONL / in-memory GraphRAG recipes

### Alias lookup

1. search `aliases.jsonl` by `alias`
2. resolve `canonical_id`
3. join `canonical-entities.jsonl`

### Source-grounded fact lookup

1. filter `canonical-claims.jsonl` by `subject_id`
2. rank by `supporting_source_count`
3. join `provenance.jsonl`
4. use `chunks.jsonl` for supporting text

### Version-aware lookup

1. resolve entity
2. collect supporting docs via `provenance.jsonl`
3. join `version-tags.jsonl`
4. filter to `lod` or `d2r` depending on user intent

## Suggested first production queries

1. “Spirit 是什么，来自哪些来源？”
2. “哪些条目目前需要 API key？”
3. “某个实体在 D2R 和 LoD 是否有版本差异？”
4. “给我这个实体的来源证据和原始 chunk”
