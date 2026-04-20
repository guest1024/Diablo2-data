#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "docs" / "tier0" / "derived"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    version_path = DERIVED / "version-tags.jsonl"
    contradiction_path = DERIVED / "contradiction-seeds.jsonl"
    manifest_path = DERIVED / "version-semantics-manifest.json"
    report_path = DERIVED / "version-semantics-report.md"

    expect(version_path.is_file(), "version tags jsonl exists")
    expect(contradiction_path.is_file(), "contradiction seeds jsonl exists")
    expect(manifest_path.is_file(), "version semantics manifest exists")
    expect(report_path.is_file(), "version semantics report exists")

    version_tags = load_jsonl(version_path)
    contradiction_seeds = load_jsonl(contradiction_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expect(len(version_tags) >= 30, "version tags cover at least all normalized docs")
    expect(len(contradiction_seeds) >= 10, "contradiction seeds provide a non-empty review set")
    expect(manifest["version_tag_count"] == len(version_tags), "manifest version tag count matches")
    expect(manifest["contradiction_seed_count"] == len(contradiction_seeds), "manifest contradiction seed count matches")
    expect(any(tag["variant"] == "lod" for tag in version_tags), "lod-tagged docs exist")
    expect(any(tag["variant"] == "d2r" or "d2r-unspecified" in tag["version_tokens"] for tag in version_tags), "d2r-tagged docs exist")
    expect(all("version_tokens" in tag and isinstance(tag["version_tokens"], list) for tag in version_tags), "all version rows include version token lists")
    expect(all("needs_review" in seed for seed in contradiction_seeds), "all contradiction seeds include review flag")

    print("PASS: version semantics verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
