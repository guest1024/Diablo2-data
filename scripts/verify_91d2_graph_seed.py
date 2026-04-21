#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/91d2-high-value/derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    manifest = BASE / "graph-seed-manifest.json"
    report = BASE / "graph-seed-report.md"
    nodes = BASE / "nodes.jsonl"
    edges = BASE / "edges.jsonl"
    claims = BASE / "claims.jsonl"
    for p, label in [(manifest, "manifest"), (report, "report"), (nodes, "nodes"), (edges, "edges"), (claims, "claims")]:
        expect(p.is_file(), f"91d2 graph {label} exists")
    m = json.loads(manifest.read_text(encoding="utf-8"))
    expect(m["node_count"] > 50, "91d2 graph node count is populated")
    expect(m["edge_count"] > 50, "91d2 graph edge count is populated")
    expect(m["claim_count"] > 50, "91d2 graph claim count is populated")
    print("PASS: 91d2 graph seed verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
