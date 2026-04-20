#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_JSON = ROOT / "docs/tier0/dataset-profile.json"
PROFILE_MD = ROOT / "docs/tier0/dataset-profile.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(PROFILE_JSON.is_file(), "dataset profile json exists")
    expect(PROFILE_MD.is_file(), "dataset profile markdown exists")
    profile = json.loads(PROFILE_JSON.read_text(encoding="utf-8"))

    expect(profile["totals"]["raw_files"] >= 20, "dataset profile raw file count looks populated")
    expect(profile["totals"]["documents"] >= 20, "dataset profile document count looks populated")
    expect(profile["totals"]["chunks"] >= profile["totals"]["documents"], "dataset profile chunks >= documents")
    expect(len(profile["by_source"]) >= 5, "dataset profile contains per-source stats")
    expect(all(stats["raw_files"] >= 1 for stats in profile["by_source"].values()), "each source has raw file coverage")
    expect("Tier 0 Dataset Profile" in PROFILE_MD.read_text(encoding="utf-8"), "dataset profile markdown has title")
    print("PASS: dataset profile verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
