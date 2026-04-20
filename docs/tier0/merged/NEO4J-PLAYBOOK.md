# Merged Graph Neo4j Playbook

Use this playbook when you want to load the merged graph directly into Neo4j.

## Input CSVs

- `docs/tier0/merged/csv/nodes.csv`
- `docs/tier0/merged/csv/edges.csv`
- `docs/tier0/merged/csv/claims.csv`
- `docs/tier0/merged/csv/chunks.csv`

## Suggested load order

1. `nodes.csv`
2. `edges.csv`
3. `claims.csv`
4. `chunks.csv`

## Minimal Cypher sketch

```cypher
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:Node {node_id: row.node_id})
SET n += row;

LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (a:Node {node_id: row.from_id})
MATCH (b:Node {node_id: row.to_id})
MERGE (a)-[r:RELATED {edge_id: row.edge_id}]->(b)
SET r.edge_type = row.edge_type;

LOAD CSV WITH HEADERS FROM 'file:///claims.csv' AS row
MATCH (n:Node {node_id: row.subject_id})
MERGE (c:Claim {claim_id: row.claim_id})
SET c += row
MERGE (n)-[:HAS_CLAIM]->(c);
```

## Practical note

This merged graph is best used as a richer retrieval/fact surface. If you need stricter canonical/provenance governance, keep the base `docs/tier0/derived/` artifacts nearby.
