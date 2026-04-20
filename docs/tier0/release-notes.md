# Tier 0 Release Notes

## Summary

- Sources captured: `5`
- Raw captures: `30`
- Normalized documents: `30`
- Retrieval chunks: `4490`
- Graph nodes / edges / claims: `272` / `397` / `79`
- Canonical entities / claims: `237` / `51`
- Aliases / provenance: `461` / `79`
- Version tags / contradiction seeds: `30` / `10`

## Deliverables

- Tier 0 raw capture + scoped inventories
- Normalized documents + retrieval chunks
- Graph seed, aliases, provenance, refined graph
- Canonical claims + relation taxonomy
- Graph export bundle + CSV export
- Neo4j import playbook + consumer guide + query recipes
- Operator pipeline, stack verify, checksum verify, status snapshot, handoff docs

## CSV export counts

- canonical_entities: `237`
- aliases: `461`
- canonical_claims: `51`
- support_edges: `16`
- provenance: `79`
- chunks: `4490`

## Known next-step work

- Cross-source entity merge rules
- Stronger contradiction modeling
- Patch/version-aware claim refinement
- Tier 1 source expansion
