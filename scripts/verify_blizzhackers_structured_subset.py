#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/tier0/raw/blizzhackers-d2data/structured-subset-manifest.json"
OUT_DIR = ROOT / "docs/tier0/raw/blizzhackers-d2data/json-files"

REQUIRED = {
    "armor.json",
    "weapons.json",
    "misc.json",
    "runes.json",
    "skills.json",
    "levels.json",
    "cubemain.json",
    "uniqueitems.json",
    "setitems.json",
    "monstats.json",
    "hireling.json",
}


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(MANIFEST.is_file(), "blizzhackers structured subset manifest exists")
    obj = json.loads(MANIFEST.read_text(encoding="utf-8"))
    files = {row["name"] for row in obj.get("files", [])}
    expect(obj.get("failed_files", 0) == 0, "blizzhackers structured subset downloaded without failures")
    expect(len(files) >= len(REQUIRED), "blizzhackers structured subset has enough files")
    for name in sorted(REQUIRED):
        expect(name in files, f"subset includes {name}")
        path = OUT_DIR / name
        expect(path.is_file(), f"downloaded file exists: {name}")
        expect(path.stat().st_size > 20, f"downloaded file is non-trivial: {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
