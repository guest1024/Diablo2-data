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
    json_path = BASE / "page-index.json"
    md_path = BASE / "page-index.md"
    expect(json_path.is_file(), "high-value page index json exists")
    expect(md_path.is_file(), "high-value page index markdown exists")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    expect(payload["total_pages"] >= 100, "page index total page count is populated")
    expect(payload["successful_pages"] >= 100, "page index successful page count is populated")
    expect(len(payload["top_pages"]) >= 20, "page index includes many top pages")
    expect(all("url" in page and "title" in page for page in payload["top_pages"][:20]), "top page entries include url and title")
    text = md_path.read_text(encoding="utf-8")
    for phrase in ("High-Value Page Index", "Successful pages", "| Source | Chars | Title | URL |"):
        expect(phrase in text, f"page index markdown contains '{phrase}'")
    print("PASS: high-value page index verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
