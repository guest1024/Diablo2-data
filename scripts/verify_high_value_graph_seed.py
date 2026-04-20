#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value/derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    nodes_path = BASE / "nodes.jsonl"
    edges_path = BASE / "edges.jsonl"
    claims_path = BASE / "claims.jsonl"
    manifest_path = BASE / "graph-seed-manifest.json"
    report_path = BASE / "graph-seed-report.md"
    expect(nodes_path.is_file(), "high-value graph nodes exist")
    expect(edges_path.is_file(), "high-value graph edges exist")
    expect(claims_path.is_file(), "high-value graph claims exist")
    expect(manifest_path.is_file(), "high-value graph manifest exists")
    expect(report_path.is_file(), "high-value graph report exists")
    nodes = load_jsonl(nodes_path)
    edges = load_jsonl(edges_path)
    claims = load_jsonl(claims_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expect(len(nodes) > 100, "high-value graph has more than 100 nodes")
    expect(len(edges) > 100, "high-value graph has more than 100 edges")
    expect(len(claims) > 100, "high-value graph has more than 100 claims")
    expect(manifest["node_count"] == len(nodes), "high-value graph manifest node count matches")
    expect(manifest["edge_count"] == len(edges), "high-value graph manifest edge count matches")
    expect(manifest["claim_count"] == len(claims), "high-value graph manifest claim count matches")
    print("PASS: high-value graph seed verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
