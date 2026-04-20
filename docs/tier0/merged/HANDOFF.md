# Merged Graph Handoff

This handoff is for downstream consumers who want to use the **merged Tier 0 graph** instead of the smaller base-only graph.

## Primary entrypoints

1. `docs/tier0/merged/export-bundle.json`
2. `docs/tier0/merged/CONSUMER-GUIDE.md`
3. `docs/tier0/merged/QUICKSTART.md`
4. `docs/tier0/merged/sample-queries.json`

## What the merged graph adds

- high-value detail pages already folded into the graph surface
- larger retrieval chunk pool
- better coverage for items, runewords, skills, monsters, and areas

## Current counts

- nodes: `925`
- edges: `1049`
- claims: `731`
- chunks: `8155`

## Recommended downstream pattern

- **Graph/fact retrieval:** use `docs/tier0/merged/`
- **Strict canonical/provenance governance:** use `docs/tier0/derived/`

## Safe next step

If you only do one thing next, import or index the merged bundle for retrieval, then join back to base canonical/provenance data for final answer grounding.
