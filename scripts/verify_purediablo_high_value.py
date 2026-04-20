#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/purediablo-high-value"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    manifest_path = BASE / "manifest.json"
    readme_path = BASE / "README.md"
    docs_path = BASE / "normalized/documents.jsonl"
    chunks_path = BASE / "derived/chunks.jsonl"
    expect(manifest_path.is_file(), "purediablo manifest exists")
    expect(readme_path.is_file(), "purediablo README exists")
    expect(docs_path.is_file(), "purediablo normalized docs exist")
    expect(chunks_path.is_file(), "purediablo chunks exist")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expect(manifest["page_count"] >= 10, "purediablo page count populated")
    expect(manifest["successful_pages"] >= 8, "purediablo successful page count is substantial")
    expect(manifest["chunk_count"] >= manifest["page_count"], "purediablo chunk count >= page count")
    expect(manifest["char_count"] > 50000, "purediablo char count is substantial")
    print("PASS: purediablo high-value verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
