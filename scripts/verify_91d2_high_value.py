#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/91d2-high-value"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    manifest_path = BASE / "manifest.json"
    readme_path = BASE / "README.md"
    docs_path = BASE / "normalized/documents.jsonl"
    chunks_path = BASE / "derived/chunks.jsonl"
    expect(manifest_path.is_file(), "91d2 manifest exists")
    expect(readme_path.is_file(), "91d2 README exists")
    expect(docs_path.is_file(), "91d2 normalized docs exist")
    expect(chunks_path.is_file(), "91d2 chunks exist")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expect(manifest["page_count"] >= 20, "91d2 page count is substantial")
    expect(manifest["chunk_count"] >= manifest["page_count"], "91d2 chunk count >= page count")
    expect(manifest["char_count"] > 150000, "91d2 char count is substantial")
    expect("jiaosezhiye" in manifest["by_category"], "91d2 contains role/build category")
    expect("jichuzhishi" in manifest["by_category"], "91d2 contains base knowledge category")
    print("PASS: 91d2 high-value verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
