#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "docs" / "tier0"
MANIFEST = OUTPUT_ROOT / "fetch-manifest.json"
REPORT = OUTPUT_ROOT / "fetch-report.md"
REGISTRY = OUTPUT_ROOT / "source-registry.json"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(REGISTRY.is_file(), "source registry exists")
    expect(MANIFEST.is_file(), "fetch manifest exists")
    expect(REPORT.is_file(), "fetch report exists")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = manifest["results"]
    expect(len(results) >= 15, "at least 15 Tier 0 capture results were recorded")

    source_ids = {entry["source_id"] for entry in results}
    for expected in {
        "arreat-summit",
        "diablo2-io",
        "blizzhackers-d2data",
        "diablo2-net-api",
        "blizzard-cn-d2",
    }:
        expect(expected in source_ids, f"{expected} has captured results")

    for entry in results:
        output = ROOT / entry["output_path"]
        expect(output.is_file(), f"captured file exists for {entry['label']}")

    report_text = REPORT.read_text(encoding="utf-8")
    expect("Tier 0 Execution Notes" in report_text, "report contains execution notes")
    expect("require an API key" in report_text or "requires an API key" in report_text, "report captures Diablo-2.net API gating")

    inventories = OUTPUT_ROOT / "url-inventories"
    expect((inventories / "arreat-summit.txt").is_file(), "arreat summit inventory exists")
    expect((inventories / "diablo2-io.txt").is_file(), "diablo2.io inventory exists")
    expect((inventories / "blizzard-cn-d2.txt").is_file(), "blizzard cn inventory exists")
    expect((inventories / "blizzhackers-d2data.txt").is_file(), "blizzhackers inventory exists")

    arreat_urls = (inventories / "arreat-summit.txt").read_text(encoding="utf-8").splitlines()
    expect(all(url.startswith("https://classic.battle.net/diablo2exp/") for url in arreat_urls), "arreat summit inventory is scoped to diablo2exp")

    diablo2io_urls = (inventories / "diablo2-io.txt").read_text(encoding="utf-8").splitlines()
    forbidden_diablo2io = [url for url in diablo2io_urls if any(bad in url for bad in ("/forums", "/trade", "/builds", "/articles", "/tools", "price-check"))]
    expect(not forbidden_diablo2io, "diablo2.io inventory excludes forbidden/noisy sections")

    blizzhackers_urls = (inventories / "blizzhackers-d2data.txt").read_text(encoding="utf-8").splitlines()
    expect(any("api.github.com/repos/blizzhackers/d2data/contents/json" in url or "raw.githubusercontent.com" in url for url in blizzhackers_urls), "blizzhackers inventory includes machine-readable discovery URLs")

    diablo2net_urls = (inventories / "diablo2-net-api.txt").read_text(encoding="utf-8").splitlines()
    expect(all(url.startswith("https://www.diablo-2.net/api") for url in diablo2net_urls), "diablo-2.net inventory stays within API scope")

    print("PASS: Tier 0 fetch verification completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
