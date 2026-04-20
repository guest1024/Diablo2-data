# Diablo II Tier 0 Stack Index

This file is the operator-facing entrypoint for the current Tier 0 acquisition / GraphRAG seed stack.

## Key counts

- Sources: `5`
- Captures: `30`
- Normalized documents: `30`
- Retrieval chunks: `4490`
- Artifact checksum entries: `14`

## Main entrypoints

- Fetch manifest: `docs/tier0/fetch-manifest.json`
- Fetch report: `docs/tier0/fetch-report.md`
- Normalized manifest: `docs/tier0/normalized-manifest.json`
- Graph export bundle: `docs/tier0/derived/graph-export-bundle.json`
- CSV export manifest: `docs/tier0/export/csv-export-manifest.json`
- Consumer guide: `docs/tier0/graph-export-consumer-guide.md`
- Neo4j playbook: `docs/tier0/neo4j-import-playbook.md`
- Operator notes: `docs/tier0/pipeline-operator-notes.md`
- Checksum manifest: `docs/tier0/artifact-checksums.json`

## One-command operations

```bash
python3 scripts/run_tier0_pipeline.py
python3 scripts/verify_tier0_stack.py
python3 scripts/verify_artifact_checksums.py
```

## Graph bundle counts

- nodes: `272`
- edges: `397`
- claims: `79`
- chunks: `4490`
- canonical_entities: `237`
- support_edges: `16`
- claim_index: `79`
- canonical_claims: `51`
- aliases: `461`
- provenance: `79`

## Version / contradiction counts

- Version tags: `30`
- Contradiction seeds: `10`

## CSV export tables

- canonical_entities: `237`
- aliases: `461`
- canonical_claims: `51`
- support_edges: `16`
- provenance: `79`
- chunks: `4490`

## Machine-readable summary

- `docs/tier0/stack-summary.json`
