#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "docs" / "tier0"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    docs_path = OUTPUT_ROOT / "normalized" / "documents.jsonl"
    chunks_path = OUTPUT_ROOT / "derived" / "chunks.jsonl"
    manifest_path = OUTPUT_ROOT / "normalized-manifest.json"
    report_path = OUTPUT_ROOT / "normalized-report.md"

    expect(docs_path.is_file(), "normalized documents jsonl exists")
    expect(chunks_path.is_file(), "derived chunks jsonl exists")
    expect(manifest_path.is_file(), "normalized manifest exists")
    expect(report_path.is_file(), "normalized report exists")

    docs = load_jsonl(docs_path)
    chunks = load_jsonl(chunks_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expect(len(docs) >= 20, "at least 20 normalized documents were produced")
    expect(len(chunks) >= len(docs), "chunk count is at least document count")
    expect(manifest["document_count"] == len(docs), "normalized manifest document count matches")
    expect(manifest["chunk_count"] == len(chunks), "normalized manifest chunk count matches")

    source_ids = {doc["source_id"] for doc in docs}
    for expected in {"arreat-summit", "diablo2-io", "blizzhackers-d2data", "diablo2-net-api", "blizzard-cn-d2"}:
        expect(expected in source_ids, f"normalized documents include {expected}")

    expect(all(doc["text"].strip() for doc in docs), "all normalized documents contain text")
    expect(any("API key" in doc["text"] or "API Key" in doc["text"] for doc in docs if doc["source_id"] == "diablo2-net-api"), "normalized docs preserve Diablo-2.net API gating evidence")
    expect(all(chunk["char_count"] > 0 for chunk in chunks), "all chunks have positive length")
    expect(all("doc_id" in chunk and "source_id" in chunk for chunk in chunks), "all chunks include doc/source linkage")

    print("PASS: Tier 0 normalization verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
