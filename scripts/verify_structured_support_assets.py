#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRUCTURED = ROOT / "docs/tier0/structured"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def main() -> int:
    manifest = STRUCTURED / "manifest.json"
    expect(manifest.is_file(), "structured support manifest exists")

    base_items = load_jsonl(STRUCTURED / "base-items.jsonl")
    runes = load_jsonl(STRUCTURED / "runes.jsonl")
    runewords = load_jsonl(STRUCTURED / "runewords.jsonl")
    unique_items = load_jsonl(STRUCTURED / "unique-items.jsonl")
    skills = load_jsonl(STRUCTURED / "skills.jsonl")
    cube_recipes = load_jsonl(STRUCTURED / "cube-recipes.jsonl")
    areas = load_jsonl(STRUCTURED / "areas.jsonl")
    monster_resistances = load_jsonl(STRUCTURED / "monster-resistances.jsonl")
    breakpoints = load_jsonl(STRUCTURED / "breakpoints.jsonl")

    expect(len(base_items) >= 350, "base items coverage is substantial")
    expect(len(runes) >= 30, "runes coverage includes full rune ladder")
    expect(len(runewords) >= 70, "runeword coverage is substantial")
    expect(len(unique_items) >= 350, "unique items coverage is substantial")
    expect(len(skills) >= 200, "skills coverage is substantial")
    expect(len(cube_recipes) >= 200, "cube recipe coverage is substantial")
    expect(len(areas) >= 100, "area coverage is substantial")
    expect(len(monster_resistances) >= 300, "monster resistance coverage is substantial")
    expect(len(breakpoints) >= 15, "breakpoint coverage is substantial")

    base_names = {row["name"] for row in base_items}
    rune_names = {row["name"] for row in runes}
    runeword_names = {row["name"] for row in runewords}
    unique_names = {row["name"] for row in unique_items}
    area_names = {row["name"] for row in areas}

    expect("Mage Plate" in base_names, "base items include Mage Plate")
    expect("Ber" in rune_names and "Jah" in rune_names and "Ith" in rune_names, "runes include Enigma ingredients")
    enigma = next((row for row in runewords if row["name"] == "Enigma"), None)
    expect(enigma is not None, "runewords include Enigma")
    expect(enigma["socket_count"] == 3, "Enigma carries the expected socket count")
    expect(set(enigma["runes_used"]) == {"r31", "r06", "r30"}, "Enigma captures Jah Ith Ber composition")
    spirit = next((row for row in runewords if row["name"] == "Spirit"), None)
    expect(spirit is not None, "runewords include Spirit")
    spirit_fcr = next((mod for mod in spirit["modifiers"] if mod["code"] == "cast3"), None)
    expect(spirit_fcr is not None and spirit_fcr["min"] == 25 and spirit_fcr["max"] == 35, "Spirit captures the 25-35 FCR roll range")
    expect("Harlequin Crest" in unique_names, "unique items include Harlequin Crest")
    expect(any(name in area_names for name in {"Pit Level 1", "The Pit Level 1", "Pit Level 2"}), "areas include Pit data")

    sorc_fcr = next((row for row in breakpoints if row["category"] == "FCR" and row["entity"] == "Sorceress"), None)
    expect(sorc_fcr is not None, "breakpoints include Sorceress FCR")
    expect(any(point["value"] == 105 for point in sorc_fcr["breakpoints"]), "Sorceress FCR includes 105 breakpoint")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
