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
    manifest_path = BASE / "manifest.json"
    report_path = BASE / "report.md"
    docs_path = BASE / "normalized/documents.jsonl"
    chunks_path = BASE / "derived/chunks.jsonl"
    expect(manifest_path.is_file(), "high-value manifest exists")
    expect(report_path.is_file(), "high-value report exists")
    expect(docs_path.is_file(), "high-value normalized docs exist")
    expect(chunks_path.is_file(), "high-value chunks exist")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expect(manifest["page_count"] >= 40, "high-value page count is at least 40")
    expect(manifest["chunk_count"] >= manifest["page_count"], "high-value chunk count >= page count")
    expect("diablo2-io" in manifest["sources"], "high-value includes diablo2-io")
    expect("arreat-summit" in manifest["sources"], "high-value includes arreat-summit")
    expect(manifest["sources"]["diablo2-io"]["chars"] > 100000, "diablo2-io high-value chars are substantial")
    expect(manifest["sources"]["arreat-summit"]["chars"] > 20000, "arreat high-value chars are substantial")

    print("PASS: high-value content verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
