#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/derived"
HIGH = ROOT / "docs/tier0/high-value/derived"
PURE = ROOT / "docs/tier0/purediablo-high-value/derived"
CN91 = ROOT / "docs/tier0/91d2-high-value/derived"
OUT = ROOT / "docs/tier0/merged"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def dedupe(rows: list[dict], key: str) -> list[dict]:
    seen = {}
    for row in rows:
        seen[row[key]] = row
    return list(seen.values())


def main() -> int:
    base_nodes = load_jsonl(BASE / "nodes.jsonl")
    base_edges = load_jsonl(BASE / "edges.jsonl")
    base_claims = load_jsonl(BASE / "claims.jsonl")
    base_chunks = load_jsonl(BASE / "chunks.jsonl")

    hv_nodes = load_jsonl(HIGH / "nodes.jsonl")
    hv_edges = load_jsonl(HIGH / "edges.jsonl")
    hv_claims = load_jsonl(HIGH / "claims.jsonl")
    hv_chunks = load_jsonl(ROOT / "docs/tier0/high-value/derived/chunks.jsonl")

    pure_nodes = load_jsonl(PURE / "nodes.jsonl")
    pure_edges = load_jsonl(PURE / "edges.jsonl")
    pure_claims = load_jsonl(PURE / "claims.jsonl")
    pure_chunks = load_jsonl(ROOT / "docs/tier0/purediablo-high-value/derived/chunks.jsonl")

    cn91_nodes = load_jsonl(CN91 / "nodes.jsonl")
    cn91_edges = load_jsonl(CN91 / "edges.jsonl")
    cn91_claims = load_jsonl(CN91 / "claims.jsonl")
    cn91_chunks = load_jsonl(ROOT / "docs/tier0/91d2-high-value/derived/chunks.jsonl")

    merged_nodes = dedupe(base_nodes + hv_nodes + pure_nodes + cn91_nodes, "node_id")
    merged_edges = dedupe(base_edges + hv_edges + pure_edges + cn91_edges, "edge_id")
    merged_claims = dedupe(base_claims + hv_claims + pure_claims + cn91_claims, "claim_id")
    merged_chunks = dedupe(base_chunks + hv_chunks + pure_chunks + cn91_chunks, "chunk_id")

    write_jsonl(OUT / "nodes.jsonl", merged_nodes)
    write_jsonl(OUT / "edges.jsonl", merged_edges)
    write_jsonl(OUT / "claims.jsonl", merged_claims)
    write_jsonl(OUT / "chunks.jsonl", merged_chunks)

    manifest = {
        "base_counts": {
            "nodes": len(base_nodes),
            "edges": len(base_edges),
            "claims": len(base_claims),
            "chunks": len(base_chunks),
        },
        "high_value_counts": {
            "nodes": len(hv_nodes),
            "edges": len(hv_edges),
            "claims": len(hv_claims),
            "chunks": len(hv_chunks),
        },
        "purediablo_counts": {
            "nodes": len(pure_nodes),
            "edges": len(pure_edges),
            "claims": len(pure_claims),
            "chunks": len(pure_chunks),
        },
        "cn91_counts": {
            "nodes": len(cn91_nodes),
            "edges": len(cn91_edges),
            "claims": len(cn91_claims),
            "chunks": len(cn91_chunks),
        },
        "merged_counts": {
            "nodes": len(merged_nodes),
            "edges": len(merged_edges),
            "claims": len(merged_claims),
            "chunks": len(merged_chunks),
        },
        "paths": {
            "nodes": "docs/tier0/merged/nodes.jsonl",
            "edges": "docs/tier0/merged/edges.jsonl",
            "claims": "docs/tier0/merged/claims.jsonl",
            "chunks": "docs/tier0/merged/chunks.jsonl",
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "report.md").write_text(
        "# Merged Tier 0 + High-Value Graph\n\n"
        f"- Base nodes / edges / claims / chunks: `{len(base_nodes)}` / `{len(base_edges)}` / `{len(base_claims)}` / `{len(base_chunks)}`\n"
        f"- High-value nodes / edges / claims / chunks: `{len(hv_nodes)}` / `{len(hv_edges)}` / `{len(hv_claims)}` / `{len(hv_chunks)}`\n"
        f"- PureDiablo nodes / edges / claims / chunks: `{len(pure_nodes)}` / `{len(pure_edges)}` / `{len(pure_claims)}` / `{len(pure_chunks)}`\n"
        f"- 91D2 nodes / edges / claims / chunks: `{len(cn91_nodes)}` / `{len(cn91_edges)}` / `{len(cn91_claims)}` / `{len(cn91_chunks)}`\n"
        f"- Merged nodes / edges / claims / chunks: `{len(merged_nodes)}` / `{len(merged_edges)}` / `{len(merged_claims)}` / `{len(merged_chunks)}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
