#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    base_docs = load_jsonl(ROOT / "docs/tier0/normalized/documents.jsonl")
    high_docs = load_jsonl(ROOT / "docs/tier0/high-value/normalized/documents.jsonl")
    pure_docs = load_jsonl(ROOT / "docs/tier0/purediablo-high-value/normalized/documents.jsonl")
    cn91_docs = load_jsonl(ROOT / "docs/tier0/91d2-high-value/normalized/documents.jsonl")

    merged = {}
    for row in base_docs + high_docs + pure_docs + cn91_docs:
        merged[row["doc_id"]] = row

    out_dir = ROOT / "docs/tier0/merged/normalized"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "documents.jsonl"
    out_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in merged.values()) + "\n", encoding="utf-8")
    manifest = {
        "document_count": len(merged),
        "paths": {
            "documents": str(out_path.relative_to(ROOT)),
        },
    }
    (ROOT / "docs/tier0/merged/normalized-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
