#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TIER0 = ROOT / "docs/tier0"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    manifest_path = TIER0 / "snapshot-manifest.json"
    expect(manifest_path.is_file(), "snapshot manifest exists")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    snapshots = manifest.get("snapshots", [])
    expect(len(snapshots) >= 20, "snapshot manifest has substantial coverage")
    expect(len(manifest.get("by_source", {})) >= 5, "snapshot manifest covers at least 5 sources")
    for row in snapshots[:10]:
        expect(all(key in row for key in ["source_id", "label", "url", "local_path", "bytes", "sha256"]), f"snapshot row has required fields: {row.get('label')}")
        expect((ROOT / row["local_path"]).is_file(), f"snapshot local path exists: {row['local_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
