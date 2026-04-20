#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "docs" / "tier0" / "derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    canonical_path = DERIVED / "canonical-entities.jsonl"
    support_path = DERIVED / "support-edges.jsonl"
    claim_index_path = DERIVED / "claim-index.jsonl"
    manifest_path = DERIVED / "refined-graph-manifest.json"
    report_path = DERIVED / "refined-graph-report.md"

    expect(canonical_path.is_file(), "canonical entities jsonl exists")
    expect(support_path.is_file(), "support edges jsonl exists")
    expect(claim_index_path.is_file(), "claim index jsonl exists")
    expect(manifest_path.is_file(), "refined graph manifest exists")
    expect(report_path.is_file(), "refined graph report exists")

    canonical = load_jsonl(canonical_path)
    support_edges = load_jsonl(support_path)
    claim_index = load_jsonl(claim_index_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expect(len(canonical) > 40, "refined graph contains more than 40 canonical entities")
    expect(len(support_edges) > 10, "refined graph contains more than 10 support edges")
    expect(len(claim_index) > 20, "refined graph contains more than 20 claim index rows")
    expect(manifest["canonical_entity_count"] == len(canonical), "manifest canonical entity count matches")
    expect(manifest["support_edge_count"] == len(support_edges), "manifest support edge count matches")
    expect(manifest["claim_index_count"] == len(claim_index), "manifest claim index count matches")

    expect(all(item["aliases"] for item in canonical if item["name"]), "named canonical entities have aliases")
    expect(any(item["node_type"] == "Runeword" for item in canonical), "canonical entities include runewords")
    expect(any(item["node_type"] == "UniqueItem" for item in canonical), "canonical entities include unique items")
    expect(all(edge["edge_type"] == "SUPPORTS_ENTITY" for edge in support_edges), "all support edges use SUPPORTS_ENTITY type")
    expect(all(edge["support_count"] > 0 for edge in support_edges), "all support edges have positive support count")
    expect(any(row["predicate"] == "api_requires_key" for row in claim_index), "claim index preserves api_requires_key rows")

    print("PASS: refined graph verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
