# Tier 0 Artifact Matrix

| Layer | Primary files | Count summary |
| --- | --- | --- |
| Fetch | `docs/tier0/fetch-manifest.json`, `docs/tier0/fetch-report.md` | sources=5, captures=30 |
| Normalized | `docs/tier0/normalized-manifest.json`, `docs/tier0/normalized/documents.jsonl` | documents=30, chunks=4490 |
| Graph seed | `docs/tier0/derived/graph-export-bundle.json` | nodes=272, edges=397, claims=79 |
| Canonical graph | `docs/tier0/derived/canonical-entities.jsonl`, `docs/tier0/derived/canonical-claims.jsonl` | canonical_entities=237, canonical_claims=51 |
| Provenance/aliases | `docs/tier0/derived/aliases.jsonl`, `docs/tier0/derived/provenance.jsonl` | aliases=461, provenance=79 |
| Export CSV | `docs/tier0/export/csv-export-manifest.json` | tables={'canonical_entities': 237, 'aliases': 461, 'canonical_claims': 51, 'support_edges': 16, 'provenance': 79, 'chunks': 4490} |
| Integrity | `docs/tier0/artifact-checksums.json`, `docs/tier0/status-snapshot.json` | checksum_entries=14 |

## Core operator commands

- `python3 scripts/run_tier0_pipeline.py`
- `python3 scripts/verify_tier0_stack.py`
- `python3 scripts/verify_artifact_checksums.py`
- `python3 scripts/verify_tier0_status_snapshot.py`

## Main handoff docs

- `docs/tier0/README.md`
- `docs/tier0/HANDOFF.md`
- `docs/tier0/graph-export-consumer-guide.md`
- `docs/tier0/neo4j-import-playbook.md`
- `docs/tier0/query-recipes.md`
