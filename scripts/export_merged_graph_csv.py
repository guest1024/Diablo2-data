#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"
OUT = MERGED / "csv"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def main() -> int:
    nodes = load_jsonl(MERGED / "nodes.jsonl")
    edges = load_jsonl(MERGED / "edges.jsonl")
    claims = load_jsonl(MERGED / "claims.jsonl")
    chunks = load_jsonl(MERGED / "chunks.jsonl")

    write_csv(
        OUT / "nodes.csv",
        nodes,
        sorted({key for row in nodes for key in row.keys()}),
    )
    write_csv(
        OUT / "edges.csv",
        edges,
        sorted({key for row in edges for key in row.keys()}),
    )
    write_csv(
        OUT / "claims.csv",
        claims,
        sorted({key for row in claims for key in row.keys()}),
    )
    write_csv(
        OUT / "chunks.csv",
        chunks,
        sorted({key for row in chunks for key in row.keys()}),
    )

    manifest = {
        "csv_tables": {
            "nodes": len(nodes),
            "edges": len(edges),
            "claims": len(claims),
            "chunks": len(chunks),
        },
        "files": {
            "nodes": "docs/tier0/merged/csv/nodes.csv",
            "edges": "docs/tier0/merged/csv/edges.csv",
            "claims": "docs/tier0/merged/csv/claims.csv",
            "chunks": "docs/tier0/merged/csv/chunks.csv",
        },
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
