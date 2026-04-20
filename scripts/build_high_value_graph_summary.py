#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value/derived"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load(BASE / "graph-seed-manifest.json")
    summary = {
        "node_count": manifest["node_count"],
        "edge_count": manifest["edge_count"],
        "claim_count": manifest["claim_count"],
        "node_types": manifest["node_types"],
        "paths": manifest["paths"],
    }
    (BASE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# High-Value Graph Summary",
        "",
        f"- Nodes: `{summary['node_count']}`",
        f"- Edges: `{summary['edge_count']}`",
        f"- Claims: `{summary['claim_count']}`",
        "",
        "## Node types",
        "",
    ]
    for node_type, count in sorted(summary["node_types"].items()):
        lines.append(f"- `{node_type}`: `{count}`")
    lines += [
        "",
        "## Main outputs",
        "",
        f"- Nodes: `{summary['paths']['nodes']}`",
        f"- Edges: `{summary['paths']['edges']}`",
        f"- Claims: `{summary['paths']['claims']}`",
        f"- Manifest: `docs/tier0/high-value/derived/graph-seed-manifest.json`",
    ]
    (BASE / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
