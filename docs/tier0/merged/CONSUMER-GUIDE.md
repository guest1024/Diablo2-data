# Merged Graph Consumer Guide

Use this guide when you want to consume the **merged** Tier 0 graph, which combines the base Tier 0 corpus with the higher-value detail-page corpus.

## Primary entrypoint

- `docs/tier0/merged/export-bundle.json`

## What the merged bundle gives you

- base Tier 0 graph coverage
- higher-value detail pages already merged in
- a larger graph/query surface than the base bundle alone

Current merged counts:

- nodes: `925`
- edges: `1049`
- claims: `731`
- chunks: `8155`

## Recommended use

Prefer the merged bundle when:

- you want higher answer quality
- you want more detailed item / runeword / skill / monster coverage
- you want retrieval to prioritize richer detail pages

Use the non-merged base bundle only when you specifically want the smaller base-only dataset.

## Files

- `docs/tier0/merged/nodes.jsonl`
- `docs/tier0/merged/edges.jsonl`
- `docs/tier0/merged/claims.jsonl`
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/export-bundle.json`

## Suggested loading order

1. `nodes.jsonl`
2. `edges.jsonl`
3. `claims.jsonl`
4. `chunks.jsonl`

## Suggested query strategy

1. resolve entity ids using the base canonical/alias layer if needed
2. use merged `claims.jsonl` for broader fact coverage
3. use merged `chunks.jsonl` for richer retrieval grounding
4. keep provenance from the base bundle when strict grounding is required

## Practical note

The merged bundle currently improves coverage and retrieval surface, but canonical/provenance/export sophistication is still richer in the base `docs/tier0/derived/` pipeline.

So the safest downstream pattern today is:

- use base canonical/alias/provenance layers for strict grounding
- use merged graph/chunks as the richer retrieval/fact surface
