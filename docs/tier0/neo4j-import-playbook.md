# Neo4j Import Playbook

This playbook shows a practical way to load the CSV exports under `docs/tier0/export/` into Neo4j.

## Required input files

- `docs/tier0/export/canonical_entities.csv`
- `docs/tier0/export/aliases.csv`
- `docs/tier0/export/canonical_claims.csv`
- `docs/tier0/export/support_edges.csv`
- `docs/tier0/export/provenance.csv`
- `docs/tier0/export/chunks.csv`

## Recommended load sequence

1. canonical entities
2. aliases
3. canonical claims
4. support edges
5. provenance
6. chunks

## Example Cypher sketch

```cypher
LOAD CSV WITH HEADERS FROM 'file:///canonical_entities.csv' AS row
MERGE (e:Entity {canonical_id: row.canonical_id})
SET e.node_type = row.node_type,
    e.key = row.key,
    e.name = row.name,
    e.aliases = split(row.aliases, '|'),
    e.document_count = toInteger(row.document_count),
    e.supporting_source_count = toInteger(row.supporting_source_count),
    e.claim_count = toInteger(row.claim_count);

LOAD CSV WITH HEADERS FROM 'file:///aliases.csv' AS row
MATCH (e:Entity {canonical_id: row.canonical_id})
MERGE (a:Alias {alias_id: row.alias_id})
SET a.alias = row.alias,
    a.alias_type = row.alias_type,
    a.node_type = row.node_type
MERGE (a)-[:ALIASES]->(e);

LOAD CSV WITH HEADERS FROM 'file:///canonical_claims.csv' AS row
MATCH (e:Entity {canonical_id: row.subject_id})
MERGE (c:Claim {canonical_claim_id: row.canonical_claim_id})
SET c.predicate = row.predicate,
    c.predicate_family = row.predicate_family,
    c.object = row.object,
    c.supporting_source_count = toInteger(row.supporting_source_count),
    c.claim_variant_count = toInteger(row.claim_variant_count)
MERGE (e)-[:HAS_CLAIM]->(c);
```

## Notes

- Keep `canonical_entities.csv` as the query-facing entity layer.
- Use `aliases.csv` for lookup expansion.
- Use `canonical_claims.csv` + `provenance.csv` to ground answers.
- Use `chunks.csv` for retrieval augmentation rather than as primary graph identity.
