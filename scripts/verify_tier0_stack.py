#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    required_files = [
        "docs/tier0/fetch-manifest.json",
        "docs/tier0/fetch-report.md",
        "docs/tier0/normalized-manifest.json",
        "docs/tier0/normalized-report.md",
        "docs/tier0/derived/graph-seed-manifest.json",
        "docs/tier0/derived/alias-seed-manifest.json",
        "docs/tier0/derived/refined-graph-manifest.json",
        "docs/tier0/derived/claim-normalization-manifest.json",
        "docs/tier0/derived/version-semantics-manifest.json",
        "docs/tier0/derived/graph-export-bundle.json",
        "docs/tier0/export/csv-export-manifest.json",
        "docs/tier0/artifact-checksums.json",
        "docs/tier0/status-snapshot.json",
        "docs/tier0/graph-export-consumer-guide.md",
        "docs/tier0/neo4j-import-playbook.md",
        "docs/tier0/pipeline-operator-notes.md",
        "docs/tier0/HANDOFF.md",
        "docs/tier0/query-recipes.md",
        "docs/tier0/artifact-matrix.md",
        "docs/tier0/sample-queries.json",
        "docs/tier0/stack-summary.json",
        "docs/tier0/readiness-checklist.md",
        "docs/tier0/release-notes.md",
        "docs/tier0/artifact-catalog.json",
        "docs/tier0/dataset-profile.json",
        "docs/tier0/dataset-profile.md",
        "docs/tier0/QUICKSTART.md",
        "docs/tier0/combined-content-stats.json",
        "docs/tier0/combined-content-stats.md",
        "docs/tier0/high-value/manifest.json",
        "docs/tier0/high-value/report.md",
        "docs/tier0/high-value/summary.json",
        "docs/tier0/high-value/README.md",
        "docs/tier0/high-value/page-index.json",
        "docs/tier0/high-value/page-index.md",
        "docs/tier0/high-value/preview.json",
        "docs/tier0/high-value/preview.md",
        "docs/tier0/high-value/derived/graph-seed-manifest.json",
        "docs/tier0/high-value/derived/graph-seed-report.md",
        "docs/tier0/high-value/derived/summary.json",
        "docs/tier0/high-value/derived/summary.md",
        "docs/tier0/merged/manifest.json",
        "docs/tier0/merged/report.md",
        "docs/tier0/merged/summary.json",
        "docs/tier0/merged/summary.md",
        "docs/tier0/merged/export-bundle.json",
        "docs/tier0/merged/export-bundle-report.md",
        "docs/tier0/merged/CONSUMER-GUIDE.md",
        "docs/tier0/merged/sample-queries.json",
        "docs/tier0/merged/normalized-manifest.json",
        "docs/tier0/merged/normalized/documents.jsonl",
        "docs/tier0/merged/aliases.jsonl",
        "docs/tier0/merged/provenance.jsonl",
        "docs/tier0/merged/canonical-entities.jsonl",
        "docs/tier0/merged/support-edges.jsonl",
        "docs/tier0/merged/claim-index.jsonl",
        "docs/tier0/merged/canonical-claims.jsonl",
        "docs/tier0/merged/relation-taxonomy.json",
    ]
    for relative in required_files:
        expect((ROOT / relative).is_file(), f"{relative} exists")

    export_bundle = json.loads((ROOT / "docs/tier0/derived/graph-export-bundle.json").read_text(encoding="utf-8"))
    csv_manifest = json.loads((ROOT / "docs/tier0/export/csv-export-manifest.json").read_text(encoding="utf-8"))

    expect(export_bundle["counts"]["canonical_entities"] == csv_manifest["csv_tables"]["canonical_entities"], "canonical entity counts align between bundle and csv export")
    expect(export_bundle["counts"]["aliases"] == csv_manifest["csv_tables"]["aliases"], "alias counts align between bundle and csv export")
    expect(export_bundle["counts"]["canonical_claims"] == csv_manifest["csv_tables"]["canonical_claims"], "canonical claim counts align between bundle and csv export")
    expect(export_bundle["counts"]["support_edges"] == csv_manifest["csv_tables"]["support_edges"], "support edge counts align between bundle and csv export")
    expect(export_bundle["counts"]["provenance"] == csv_manifest["csv_tables"]["provenance"], "provenance counts align between bundle and csv export")
    expect(export_bundle["counts"]["chunks"] == csv_manifest["csv_tables"]["chunks"], "chunk counts align between bundle and csv export")

    checksum_manifest = json.loads((ROOT / "docs/tier0/artifact-checksums.json").read_text(encoding="utf-8"))
    expect(checksum_manifest["artifact_count"] >= 10, "artifact checksum manifest covers multiple key outputs")

    print("PASS: Tier 0 stack verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
