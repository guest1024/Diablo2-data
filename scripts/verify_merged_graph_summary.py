#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    summary_json = MERGED / "summary.json"
    summary_md = MERGED / "summary.md"
    expect(summary_json.is_file(), "merged graph summary json exists")
    expect(summary_md.is_file(), "merged graph summary markdown exists")
    payload = json.loads(summary_json.read_text(encoding="utf-8"))
    expect(payload["merged_counts"]["nodes"] >= payload["base_counts"]["nodes"], "merged node count summary is valid")
    expect(payload["merged_counts"]["chunks"] >= payload["base_counts"]["chunks"], "merged chunk count summary is valid")
    text = summary_md.read_text(encoding="utf-8")
    for phrase in ("Merged Graph Summary", "Outputs", "Merged nodes / edges / claims / chunks"):
        expect(phrase in text, f"merged graph summary contains '{phrase}'")
    print("PASS: merged graph summary verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
