#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def main() -> int:
    alias_path = ROOT / "docs/tier0/alias-registry.jsonl"
    eq_path = ROOT / "docs/tier0/term-equivalence.jsonl"
    builds_path = ROOT / "docs/tier0/build-archetypes.jsonl"

    expect(alias_path.is_file(), "alias registry exists")
    expect(eq_path.is_file(), "term equivalence registry exists")
    expect(builds_path.is_file(), "build archetypes registry exists")

    aliases = load_jsonl(alias_path)
    equivalences = load_jsonl(eq_path)
    builds = load_jsonl(builds_path)

    expect(len(aliases) > 100, "alias registry has substantial coverage")
    expect(len(equivalences) > 50, "term equivalence registry has substantial coverage")
    expect(len(builds) >= 5, "build archetype registry has starter coverage")
    expect(all(row.get("alias_id") for row in aliases), "alias registry rows all have alias_id")
    expect(all(row.get("edge_id") for row in equivalences), "term equivalence rows all have edge_id")
    expect(all(":::" not in row["alias_id"] for row in aliases), "alias ids do not contain malformed separators")
    expect(all(":::" not in row["edge_id"] for row in equivalences), "term equivalence ids do not contain malformed separators")

    required_aliases = {"SOJ", "CTA", "HOTO", "MF", "DClone", "安头", "米山", "锤丁"}
    present_aliases = {row["alias"] for row in aliases}
    for alias in required_aliases:
        expect(alias in present_aliases, f"alias registry contains {alias}")

    required_build_ids = {
        "build::javazon",
        "build::hammerdin",
        "build::lightning-sorceress",
        "build::blizzard-sorceress",
        "build::summon-necromancer",
    }
    present_build_ids = {row["build_id"] for row in builds}
    for build_id in required_build_ids:
        expect(build_id in present_build_ids, f"build registry contains {build_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
