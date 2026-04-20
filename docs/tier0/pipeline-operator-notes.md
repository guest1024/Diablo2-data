# Tier 0 Pipeline Operator Notes

## One-command rerun

Use:

```bash
python3 scripts/run_tier0_pipeline.py
```

This reruns the complete Tier 0 stack:

1. fetch
2. normalized documents/chunks
3. graph seed
4. alias/provenance seed
5. refined graph
6. claim normalization
7. version semantics
8. graph export bundle
9. CSV export
10. artifact checksum manifest

## One-command stack verification

Use:

```bash
python3 scripts/verify_tier0_stack.py
```

This checks:

- all top-level manifest/report artifacts exist
- bundle counts align with CSV export counts
- downstream consumer docs are present
- artifact checksum manifest exists and is included in top-level verification

## Dry run

To inspect the pipeline sequence without executing:

```bash
python3 scripts/run_tier0_pipeline.py --dry-run
```
