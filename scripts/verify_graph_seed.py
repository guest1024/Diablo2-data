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
    nodes_path = DERIVED / "nodes.jsonl"
    edges_path = DERIVED / "edges.jsonl"
    claims_path = DERIVED / "claims.jsonl"
    manifest_path = DERIVED / "graph-seed-manifest.json"
    report_path = DERIVED / "graph-seed-report.md"

    expect(nodes_path.is_file(), "graph nodes jsonl exists")
    expect(edges_path.is_file(), "graph edges jsonl exists")
    expect(claims_path.is_file(), "graph claims jsonl exists")
    expect(manifest_path.is_file(), "graph seed manifest exists")
    expect(report_path.is_file(), "graph seed report exists")

    nodes = load_jsonl(nodes_path)
    edges = load_jsonl(edges_path)
    claims = load_jsonl(claims_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expect(len(nodes) > 50, "graph seed contains more than 50 nodes")
    expect(len(edges) > 50, "graph seed contains more than 50 edges")
    expect(len(claims) > 20, "graph seed contains more than 20 claims")
    expect(manifest["node_count"] == len(nodes), "manifest node count matches")
    expect(manifest["edge_count"] == len(edges), "manifest edge count matches")
    expect(manifest["claim_count"] == len(claims), "manifest claim count matches")

    node_types = {node["node_type"] for node in nodes}
    for expected in {"Source", "SourceDocument", "ApiEndpoint", "OpenDataResource"}:
        expect(expected in node_types, f"graph seed includes node type {expected}")

    edge_types = {edge["edge_type"] for edge in edges}
    for expected in {"BELONGS_TO_SOURCE", "DESCRIBES", "DISCOVERS_URL"}:
        expect(expected in edge_types, f"graph seed includes edge type {expected}")

    expect(any(claim["predicate"] == "api_requires_key" for claim in claims), "graph seed preserves API key gating claim")
    expect(all("from_id" in edge and "to_id" in edge for edge in edges), "all edges include endpoints")

    print("PASS: graph seed verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
