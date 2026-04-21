#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/chroma-ready"
MERGED = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    manifest_path = BASE / "manifest.json"
    docs_path = BASE / "documents.jsonl"
    chunks_path = BASE / "chunks.jsonl"
    readme_path = BASE / "README.md"
    expect(manifest_path.is_file(), "chroma manifest exists")
    expect(docs_path.is_file(), "chroma documents exist")
    expect(chunks_path.is_file(), "chroma chunks exist")
    expect(readme_path.is_file(), "chroma README exists")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    docs = load_jsonl(docs_path)
    chunks = load_jsonl(chunks_path)
    merged_docs = load_jsonl(MERGED / "normalized/documents.jsonl")
    merged_chunks = load_jsonl(MERGED / "chunks.jsonl")
    expect(len(docs) == manifest["documents"], "chroma document count matches manifest")
    expect(len(chunks) == manifest["chunks"], "chroma chunk count matches manifest")
    expect(len(docs) == len(merged_docs), "chroma documents stay aligned with merged normalized documents")
    expect(len(chunks) == len(merged_chunks), "chroma chunks stay aligned with merged chunks")
    expect(all({"id", "content", "metadata"} <= row.keys() for row in docs[:10]), "chroma documents use unified schema")
    expect(all({"id", "content", "metadata"} <= row.keys() for row in chunks[:10]), "chroma chunks use unified schema")
    expect(all("language" in row["metadata"] for row in chunks[:10]), "chroma chunks include language metadata")
    expect(all("doc_type" in row["metadata"] for row in chunks[:10]), "chroma chunks include doc_type metadata")
    expect(all("game_variant" in row["metadata"] for row in chunks[:10]), "chroma chunks include game_variant metadata")
    print("PASS: chroma package verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
