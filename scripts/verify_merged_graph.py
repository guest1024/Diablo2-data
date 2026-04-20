#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/tier0/merged"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def count_jsonl(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def main() -> int:
    manifest_path = OUT / "manifest.json"
    report_path = OUT / "report.md"
    expect(manifest_path.is_file(), "merged graph manifest exists")
    expect(report_path.is_file(), "merged graph report exists")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for key, rel in manifest["paths"].items():
        path = ROOT / rel
        expect(path.is_file(), f"merged {key} file exists")
        expect(count_jsonl(path) == manifest["merged_counts"][key], f"merged {key} count matches manifest")

    expect(manifest["merged_counts"]["nodes"] >= manifest["base_counts"]["nodes"], "merged node count >= base node count")
    expect(manifest["merged_counts"]["edges"] >= manifest["base_counts"]["edges"], "merged edge count >= base edge count")
    expect(manifest["merged_counts"]["claims"] >= manifest["base_counts"]["claims"], "merged claim count >= base claim count")
    expect(manifest["merged_counts"]["chunks"] >= manifest["base_counts"]["chunks"], "merged chunk count >= base chunk count")
    expect(manifest["merged_counts"]["nodes"] > manifest["base_counts"]["nodes"], "merged nodes increased after adding high-value graph")
    expect(manifest["merged_counts"]["chunks"] > manifest["base_counts"]["chunks"], "merged chunks increased after adding high-value corpus")
    print("PASS: merged graph verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
