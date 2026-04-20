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
    md = BASE / "preview.md"
    js = BASE / "preview.json"
    expect(md.is_file(), "high-value preview markdown exists")
    expect(js.is_file(), "high-value preview json exists")
    payload = json.loads(js.read_text(encoding="utf-8"))
    items = payload["items"]
    expect(len(items) >= 20, "high-value preview contains at least 20 items")
    expect(all(item["chars"] > 5000 for item in items[:10]), "top 10 preview items are substantial pages")
    expect(all(item["excerpt"] for item in items[:10]), "top 10 preview items contain excerpts")
    text = md.read_text(encoding="utf-8")
    expect("High-Value Content Preview" in text, "preview markdown title present")
    expect("Source:" in text and "URL:" in text, "preview markdown contains source and url lines")
    print("PASS: high-value preview verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
