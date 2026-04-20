#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value/derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    json_path = BASE / "summary.json"
    md_path = BASE / "summary.md"
    expect(json_path.is_file(), "high-value graph summary json exists")
    expect(md_path.is_file(), "high-value graph summary markdown exists")
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    expect(payload["node_count"] >= 100, "high-value graph summary node count is populated")
    expect(payload["edge_count"] >= 100, "high-value graph summary edge count is populated")
    expect(payload["claim_count"] >= 100, "high-value graph summary claim count is populated")
    expect("Runeword" in payload["node_types"], "high-value graph summary includes Runeword nodes")
    expect("UniqueItem" in payload["node_types"], "high-value graph summary includes UniqueItem nodes")
    text = md_path.read_text(encoding="utf-8")
    for phrase in ("High-Value Graph Summary", "Node types", "Main outputs"):
        expect(phrase in text, f"high-value graph summary markdown contains '{phrase}'")
    print("PASS: high-value graph summary verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
