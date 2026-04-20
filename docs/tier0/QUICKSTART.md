# Tier 0 Quickstart

If you are new to this repository, use this file first.

## 1. Rebuild the full Tier 0 package

```bash
python3 scripts/run_tier0_pipeline.py
```

## 2. Verify the package

```bash
python3 scripts/verify_tier0_stack.py
python3 scripts/verify_artifact_checksums.py
```

## 3. Read the key docs

Start here:

1. `docs/tier0/README.md`
2. `docs/tier0/HANDOFF.md`
3. `docs/tier0/graph-export-consumer-guide.md`
4. `docs/tier0/neo4j-import-playbook.md`
5. `docs/tier0/query-recipes.md`

## 4. Use the data

- JSONL graph bundle: `docs/tier0/derived/graph-export-bundle.json`
- CSV export: `docs/tier0/export/csv-export-manifest.json`
- Sample queries: `docs/tier0/sample-queries.json`

## 5. Check readiness

- `docs/tier0/status-snapshot.json`
- `docs/tier0/readiness-checklist.md`
- `docs/tier0/release-notes.md`

## 6. Next recommended work

- cross-source entity merge
- contradiction modeling
- patch/version-aware claim refinement
- Tier 1 source expansion
