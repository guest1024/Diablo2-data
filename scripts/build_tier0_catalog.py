#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"


CATEGORIES = {
    "manifest": [
        "docs/tier0/fetch-manifest.json",
        "docs/tier0/normalized-manifest.json",
        "docs/tier0/derived/graph-seed-manifest.json",
        "docs/tier0/derived/alias-seed-manifest.json",
        "docs/tier0/derived/refined-graph-manifest.json",
        "docs/tier0/derived/claim-normalization-manifest.json",
        "docs/tier0/derived/version-semantics-manifest.json",
        "docs/tier0/derived/graph-export-bundle.json",
        "docs/tier0/export/csv-export-manifest.json",
        "docs/tier0/artifact-checksums.json",
        "docs/tier0/stack-summary.json",
        "docs/tier0/status-snapshot.json",
    ],
    "documentation": [
        "docs/tier0/README.md",
        "docs/tier0/HANDOFF.md",
        "docs/tier0/release-notes.md",
        "docs/tier0/readiness-checklist.md",
        "docs/tier0/graph-export-consumer-guide.md",
        "docs/tier0/neo4j-import-playbook.md",
        "docs/tier0/pipeline-operator-notes.md",
        "docs/tier0/query-recipes.md",
        "docs/tier0/artifact-matrix.md",
    ],
    "query_examples": [
        "docs/tier0/sample-queries.json",
    ],
}


def main() -> int:
    entries = []
    for category, paths in CATEGORIES.items():
        for relative in paths:
            path = ROOT / relative
            entries.append(
                {
                    "path": relative,
                    "category": category,
                    "exists": path.is_file(),
                    "size": path.stat().st_size if path.exists() else 0,
                }
            )
    raw_count = sum(1 for _ in (TIER0 / "raw").rglob("*") if _.is_file())
    derived_count = sum(1 for _ in (TIER0 / "derived").rglob("*") if _.is_file())
    export_count = sum(1 for _ in (TIER0 / "export").rglob("*") if _.is_file())

    payload = {
        "entries": entries,
        "counts": {
            "cataloged": len(entries),
            "raw_files": raw_count,
            "derived_files": derived_count,
            "export_files": export_count,
        },
    }
    (TIER0 / "artifact-catalog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
