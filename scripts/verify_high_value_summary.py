#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    summary_path = BASE / "summary.json"
    readme_path = BASE / "README.md"
    expect(summary_path.is_file(), "high-value summary json exists")
    expect(readme_path.is_file(), "high-value README exists")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    expect(summary["page_count"] >= 40, "high-value summary page count is populated")
    expect(summary["successful_page_count"] >= 30, "high-value successful page count is substantial")
    expect(summary["chunk_count"] >= summary["successful_page_count"], "high-value chunks >= successful pages")
    expect("diablo2-io" in summary["sources"], "high-value summary includes diablo2-io")
    expect("arreat-summit" in summary["sources"], "high-value summary includes arreat-summit")
    text = readme_path.read_text(encoding="utf-8")
    for phrase in ["High-Value Corpus Summary", "By source", "Main outputs"]:
        expect(phrase in text, f"high-value README contains '{phrase}'")
    print("PASS: high-value summary verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
