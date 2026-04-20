#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def main() -> int:
    files = {
        "nodes": MERGED / "nodes.jsonl",
        "edges": MERGED / "edges.jsonl",
        "claims": MERGED / "claims.jsonl",
        "chunks": MERGED / "chunks.jsonl",
    }
    counts = {name: count_jsonl(path) for name, path in files.items()}
    bundle = {
        "bundle_name": "diablo2-tier0-merged-graph-export",
        "paths": {name: str(path.relative_to(ROOT)) for name, path in files.items()},
        "counts": counts,
        "recommended_load_order": ["nodes", "edges", "claims", "chunks"],
        "recommended_query_entrypoints": {
            "graph_lookup": ["nodes", "edges", "claims"],
            "retrieval": ["chunks"],
        },
    }
    (MERGED / "export-bundle.json").write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (MERGED / "export-bundle-report.md").write_text(
        "# Merged Graph Export Bundle\n\n"
        f"- Bundle: `{bundle['bundle_name']}`\n"
        f"- Nodes: `{counts['nodes']}`\n"
        f"- Edges: `{counts['edges']}`\n"
        f"- Claims: `{counts['claims']}`\n"
        f"- Chunks: `{counts['chunks']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
