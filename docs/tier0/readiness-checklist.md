# Tier 0 Readiness Checklist

Use this checklist before handing Tier 0 to another operator or downstream ingestion system.

## Data readiness

- [x] Tier 0 public-source capture exists
- [x] Scoped source inventories exist
- [x] Normalized documents exist
- [x] Retrieval chunks exist

## Graph readiness

- [x] Graph seed nodes / edges / claims exist
- [x] Alias and provenance seeds exist
- [x] Refined graph artifacts exist
- [x] Canonical claims and relation taxonomy exist
- [x] Version semantics and contradiction seeds exist

## Export readiness

- [x] Graph export bundle exists
- [x] CSV export exists
- [x] Neo4j playbook exists
- [x] Consumer guide exists
- [x] Query recipes exist
- [x] Sample query outputs exist

## Operator readiness

- [x] One-command pipeline exists
- [x] Stack verification exists
- [x] Artifact checksum verification exists
- [x] Top-level README exists
- [x] HANDOFF exists
- [x] Status snapshot exists
- [x] Artifact matrix exists

## Residual Tier 1 work

- [ ] Cross-source entity merge rules
- [ ] Stronger contradiction modeling
- [ ] Better semantic cleanup for HTML-derived text
- [ ] Patch/version-aware claim refinement
- [ ] Expansion into Tier 1 sources
