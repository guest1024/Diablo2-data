#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs" / "tier0"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    fetch = load_json(TIER0 / "fetch-manifest.json")
    docs = load_jsonl(TIER0 / "normalized" / "documents.jsonl")
    chunks = load_jsonl(TIER0 / "derived" / "chunks.jsonl")

    raw_files = list((TIER0 / "raw").rglob("*"))
    raw_files = [path for path in raw_files if path.is_file()]

    raw_by_source: dict[str, dict[str, int]] = defaultdict(lambda: {"files": 0, "bytes": 0})
    for item in fetch["results"]:
        source_id = item["source_id"]
        local_path = ROOT / item["output_path"]
        raw_by_source[source_id]["files"] += 1
        if local_path.exists():
            raw_by_source[source_id]["bytes"] += local_path.stat().st_size

    docs_by_source = Counter(doc["source_id"] for doc in docs)
    chunks_by_source = Counter(chunk["source_id"] for chunk in chunks)

    payload = {
        "totals": {
            "raw_files": len(raw_files),
            "raw_bytes": sum(path.stat().st_size for path in raw_files),
            "documents": len(docs),
            "chunks": len(chunks),
        },
        "by_source": {
            source["id"]: {
                "source_name": source["name"],
                "raw_files": raw_by_source[source["id"]]["files"],
                "raw_bytes": raw_by_source[source["id"]]["bytes"],
                "documents": docs_by_source[source["id"]],
                "chunks": chunks_by_source[source["id"]],
            }
            for source in fetch["sources"]
        },
    }

    (TIER0 / "dataset-profile.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Tier 0 Dataset Profile",
        "",
        f"- Raw files: `{payload['totals']['raw_files']}`",
        f"- Raw bytes: `{payload['totals']['raw_bytes']}`",
        f"- Documents: `{payload['totals']['documents']}`",
        f"- Chunks: `{payload['totals']['chunks']}`",
        "",
        "| Source | Raw files | Raw bytes | Documents | Chunks |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for source_id, stats in payload["by_source"].items():
        lines.append(
            f"| {stats['source_name']} | {stats['raw_files']} | {stats['raw_bytes']} | {stats['documents']} | {stats['chunks']} |"
        )
    (TIER0 / "dataset-profile.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
