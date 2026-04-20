# Tier 0 Graph Export Consumer Guide

This guide explains how to consume the Tier 0 Diablo II graph bundle under `docs/tier0/derived/` in downstream systems such as Neo4j, a property-graph ETL pipeline, or a GraphRAG ingestion workflow.

## Bundle entrypoint

Start from:

- `docs/tier0/derived/graph-export-bundle.json`

That file defines:

- file inventory
- row counts
- schema groupings
- recommended load order
- query entrypoints
- example query pipelines

## Recommended load order

Load tables in this order:

1. `nodes.jsonl`
2. `canonical-entities.jsonl`
3. `aliases.jsonl`
4. `edges.jsonl`
5. `support-edges.jsonl`
6. `claims.jsonl`
7. `canonical-claims.jsonl`
8. `provenance.jsonl`
9. `chunks.jsonl`
10. `claim-index.jsonl`

Rationale:

- entity identity should exist before relation rows
- aliases should exist before alias-driven entity resolution
- claims/provenance should load before query-time grounding
- chunks can load later because they are retrieval surfaces, not identity surfaces

## Table roles

### Identity layer

- `nodes.jsonl`: raw graph nodes from extraction
- `canonical-entities.jsonl`: query-facing canonical entity catalog
- `aliases.jsonl`: alias expansion / lookup surface

Use this layer for:

- alias resolution
- canonical entity lookup
- entity-type filtering

### Relation layer

- `edges.jsonl`: extracted graph edges
- `support-edges.jsonl`: explicit source -> entity support edges
- `claims.jsonl`: raw claim rows
- `canonical-claims.jsonl`: deduplicated/query-facing claims
- `provenance.jsonl`: evidence linkage for claims

Use this layer for:

- source-aware fact lookup
- authority-aware reranking
- provenance display
- contradiction handling extensions

### Retrieval layer

- `chunks.jsonl`: retrieval text units
- `claim-index.jsonl`: predicate/object-oriented lookup index

Use this layer for:

- semantic retrieval
- hybrid graph + chunk lookup
- answer grounding

## Suggested Neo4j mapping

### Nodes

- `Source`
- `SourceDocument`
- canonical entity node types such as:
  - `Runeword`
  - `UniqueItem`
  - `SetItem`
  - `Monster`
  - `Area`
  - `Quest`
  - `ApiEndpoint`
  - `OpenDataResource`

### Relationships

- `BELONGS_TO_SOURCE`
- `DESCRIBES`
- `DISCOVERS_URL`
- `SUPPORTS_ENTITY`

### Claim/provenance modeling options

#### Option A — property-heavy

Store canonical claims as relationship properties or attached claim documents.

Best when:

- you want fewer graph objects
- query simplicity matters more than full auditability

#### Option B — claim nodes

Create `Claim` nodes from `canonical-claims.jsonl` and attach:

- `(entity)-[:HAS_CLAIM]->(claim)`
- `(claim)-[:SUPPORTED_BY]->(source)`
- `(claim)-[:EVIDENCED_BY]->(document)`

Best when:

- provenance matters
- contradiction support will be added later
- you want graph-native answer grounding

For this project, **Option B is the better long-term fit**.

## Suggested GraphRAG lookup flow

### 1. Alias resolution

Resolve user terms through `aliases.jsonl`.

Example:

- user asks: `Spirit`
- lookup alias `Spirit`
- resolve canonical entity id
- join to `canonical-entities.jsonl`

### 2. Claim retrieval

Pull matching rows from:

- `canonical-claims.jsonl`
- `claim-index.jsonl`

Prefer:

- higher `supporting_source_count`
- stronger source classes from `provenance.jsonl`

### 3. Retrieval grounding

Use:

- `chunks.jsonl`
- `provenance.jsonl`

to retrieve supporting source text snippets.

### 4. Answer synthesis

Return:

- canonical entity
- normalized claims
- evidence URLs
- source authority notes

## Minimal import strategy

If you want the fastest path into a downstream graph system:

1. Load `canonical-entities.jsonl`
2. Load `aliases.jsonl`
3. Load `canonical-claims.jsonl`
4. Load `provenance.jsonl`
5. Load `chunks.jsonl`

This gives you:

- stable entity identity
- alias lookup
- claim retrieval
- source grounding
- chunk-based answer support

without needing the full raw graph first.

## Recommended next expansion

The current bundle is strong enough for a Tier 0 seed, but the next useful upgrades are:

1. cross-source entity merge rules
2. stronger typed relations beyond discovery/support
3. contradiction modeling
4. patch/version-aware claim normalization
5. better semantic cleanup for noisy HTML-derived text

## Files to hand to your downstream pipeline

Minimum:

- `docs/tier0/derived/graph-export-bundle.json`
- `docs/tier0/derived/canonical-entities.jsonl`
- `docs/tier0/derived/aliases.jsonl`
- `docs/tier0/derived/canonical-claims.jsonl`
- `docs/tier0/derived/provenance.jsonl`
- `docs/tier0/derived/chunks.jsonl`

Full bundle:

- all files referenced by `graph-export-bundle.json`
