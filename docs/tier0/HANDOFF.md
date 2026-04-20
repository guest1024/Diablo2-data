# Tier 0 Handoff

This document is the shortest practical handoff for taking the current Diablo II knowledge-base stack into the next execution phase.

## What already exists

The Tier 0 stack already provides:

- scoped public-source capture
- normalized documents
- retrieval chunks
- graph seed nodes / edges / claims
- aliases and provenance
- refined graph artifacts
- canonical claims and relation taxonomy
- version tags and contradiction seeds
- graph export bundle
- Neo4j-ready CSV exports
- operator pipeline + verification + checksums

## Start here

Read in this order:

1. `docs/tier0/README.md`
2. `docs/tier0/graph-export-consumer-guide.md`
3. `docs/tier0/neo4j-import-playbook.md`
4. `docs/tier0/derived/graph-export-bundle.json`

## One-command rerun

```bash
python3 scripts/run_tier0_pipeline.py
python3 scripts/verify_tier0_stack.py
python3 scripts/verify_artifact_checksums.py
```

## Most important current artifacts

### Query-facing graph layer
- `docs/tier0/derived/canonical-entities.jsonl`
- `docs/tier0/derived/aliases.jsonl`
- `docs/tier0/derived/canonical-claims.jsonl`
- `docs/tier0/derived/provenance.jsonl`
- `docs/tier0/derived/chunks.jsonl`

### Export / downstream integration
- `docs/tier0/derived/graph-export-bundle.json`
- `docs/tier0/export/canonical_entities.csv`
- `docs/tier0/export/aliases.csv`
- `docs/tier0/export/canonical_claims.csv`
- `docs/tier0/export/support_edges.csv`
- `docs/tier0/export/provenance.csv`
- `docs/tier0/export/chunks.csv`

## Recommended next Tier 1 work

1. cross-source entity merge rules
2. contradiction modeling beyond placeholder seeds
3. stronger typed relations beyond discovery/support
4. patch/version-aware claim normalization
5. better HTML cleanup for retrieval quality
6. incremental crawler expansion to Tier 1 sources

## Recommended minimal Tier 1 milestone

If you only do one next thing, do this:

- load the current export bundle into your graph system
- use aliases + canonical entities + canonical claims + provenance + chunks as the first retrieval layer
- then add cross-source merge + contradiction handling

## Operational note

This repo is not a git repository, so commit-based workflow assumptions do not apply here. The current integrity anchor is:

- `docs/tier0/artifact-checksums.json`

## Success condition for handoff

The next operator should be able to:

1. rerun the full Tier 0 pipeline
2. verify the stack
3. locate the graph bundle
4. import CSVs into Neo4j
5. identify the most important Tier 1 follow-up work
