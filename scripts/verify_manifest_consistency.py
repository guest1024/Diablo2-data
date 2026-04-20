#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"
DERIVED = TIER0 / "derived"
EXPORT = TIER0 / "export"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    fetch = load(TIER0 / "fetch-manifest.json")
    normalized = load(TIER0 / "normalized-manifest.json")
    graph_bundle = load(DERIVED / "graph-export-bundle.json")
    version_semantics = load(DERIVED / "version-semantics-manifest.json")
    csv_manifest = load(EXPORT / "csv-export-manifest.json")
    stack_summary = load(TIER0 / "stack-summary.json")
    status_snapshot = load(TIER0 / "status-snapshot.json")

    expect(stack_summary["sources"] == len(fetch["sources"]), "stack summary sources match fetch manifest")
    expect(stack_summary["captures"] == len(fetch["results"]), "stack summary captures match fetch manifest")
    expect(stack_summary["documents"] == normalized["document_count"], "stack summary documents match normalized manifest")
    expect(stack_summary["chunks"] == normalized["chunk_count"], "stack summary chunks match normalized manifest")
    expect(stack_summary["graph_counts"] == graph_bundle["counts"], "stack summary graph counts match export bundle")
    expect(stack_summary["version_semantics"]["version_tags"] == version_semantics["version_tag_count"], "stack summary version tag count matches")
    expect(stack_summary["version_semantics"]["contradiction_seeds"] == version_semantics["contradiction_seed_count"], "stack summary contradiction seed count matches")
    expect(stack_summary["csv_tables"] == csv_manifest["csv_tables"], "stack summary csv table counts match csv manifest")

    snapshot_counts = status_snapshot["counts"]
    expect(snapshot_counts["sources"] == len(fetch["sources"]), "status snapshot sources match fetch manifest")
    expect(snapshot_counts["captures"] == len(fetch["results"]), "status snapshot captures match fetch manifest")
    expect(snapshot_counts["documents"] == normalized["document_count"], "status snapshot documents match normalized manifest")
    expect(snapshot_counts["chunks"] == normalized["chunk_count"], "status snapshot chunks match normalized manifest")
    expect(snapshot_counts["graph"] == graph_bundle["counts"], "status snapshot graph counts match export bundle")
    expect(snapshot_counts["version_semantics"]["version_tags"] == version_semantics["version_tag_count"], "status snapshot version tag count matches")
    expect(snapshot_counts["version_semantics"]["contradiction_seeds"] == version_semantics["contradiction_seed_count"], "status snapshot contradiction seed count matches")
    expect(snapshot_counts["csv_export"] == csv_manifest["csv_tables"], "status snapshot csv export counts match csv manifest")

    print("PASS: manifest consistency verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
