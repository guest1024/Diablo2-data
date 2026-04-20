#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "docs/tier0/combined-content-stats.json"
MD_PATH = ROOT / "docs/tier0/combined-content-stats.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(JSON_PATH.is_file(), "combined content stats json exists")
    expect(MD_PATH.is_file(), "combined content stats markdown exists")
    payload = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    expect(payload["base_documents"] >= 30, "base document count looks populated")
    expect(payload["base_chunks"] >= 4000, "base chunk count looks populated")
    expect(payload["high_value_pages"] >= 100, "high-value page count looks populated")
    expect(payload["high_value_successful_pages"] >= 100, "high-value successful page count looks populated")
    expect(payload["high_value_chunks"] >= payload["high_value_successful_pages"], "high-value chunks >= successful pages")
    expect(payload["combined_chars"] > payload["base_chars"], "combined chars exceed base chars")
    expect(payload["combined_chunk_surfaces"] > payload["base_chunks"], "combined chunk surfaces exceed base chunks")
    text = MD_PATH.read_text(encoding="utf-8")
    for phrase in ("Base normalized documents", "High-value pages", "Combined chars", "Combined chunk surfaces"):
        expect(phrase in text, f"combined stats markdown contains '{phrase}'")
    print("PASS: combined content stats verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
