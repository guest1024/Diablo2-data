#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"
DERIVED = TIER0 / "derived"
EXPORT = TIER0 / "export"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    fetch = load_json(TIER0 / "fetch-manifest.json")
    normalized = load_json(TIER0 / "normalized-manifest.json")
    bundle = load_json(DERIVED / "graph-export-bundle.json")
    csv_manifest = load_json(EXPORT / "csv-export-manifest.json")
    checksum = load_json(TIER0 / "artifact-checksums.json")

    lines = [
        "# Tier 0 Artifact Matrix",
        "",
        "| Layer | Primary files | Count summary |",
        "| --- | --- | --- |",
        f"| Fetch | `docs/tier0/fetch-manifest.json`, `docs/tier0/fetch-report.md` | sources={len(fetch['sources'])}, captures={len(fetch['results'])} |",
        f"| Normalized | `docs/tier0/normalized-manifest.json`, `docs/tier0/normalized/documents.jsonl` | documents={normalized['document_count']}, chunks={normalized['chunk_count']} |",
        f"| Graph seed | `docs/tier0/derived/graph-export-bundle.json` | nodes={bundle['counts']['nodes']}, edges={bundle['counts']['edges']}, claims={bundle['counts']['claims']} |",
        f"| Canonical graph | `docs/tier0/derived/canonical-entities.jsonl`, `docs/tier0/derived/canonical-claims.jsonl` | canonical_entities={bundle['counts']['canonical_entities']}, canonical_claims={bundle['counts']['canonical_claims']} |",
        f"| Provenance/aliases | `docs/tier0/derived/aliases.jsonl`, `docs/tier0/derived/provenance.jsonl` | aliases={bundle['counts']['aliases']}, provenance={bundle['counts']['provenance']} |",
        f"| Export CSV | `docs/tier0/export/csv-export-manifest.json` | tables={csv_manifest['csv_tables']} |",
        f"| Integrity | `docs/tier0/artifact-checksums.json`, `docs/tier0/status-snapshot.json` | checksum_entries={checksum['artifact_count']} |",
        "",
        "## Core operator commands",
        "",
        "- `python3 scripts/run_tier0_pipeline.py`",
        "- `python3 scripts/verify_tier0_stack.py`",
        "- `python3 scripts/verify_artifact_checksums.py`",
        "- `python3 scripts/verify_tier0_status_snapshot.py`",
        "",
        "## Main handoff docs",
        "",
        "- `docs/tier0/README.md`",
        "- `docs/tier0/HANDOFF.md`",
        "- `docs/tier0/graph-export-consumer-guide.md`",
        "- `docs/tier0/neo4j-import-playbook.md`",
        "- `docs/tier0/query-recipes.md`",
    ]
    (TIER0 / "artifact-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
