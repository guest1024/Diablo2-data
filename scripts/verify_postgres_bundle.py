#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/tier0/postgres-bundle/manifest.json"
IMPORT_SQL = ROOT / "docs/tier0/postgres-bundle/import.sql"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


csv.field_size_limit(sys.maxsize)


def main() -> int:
    expect(MANIFEST.is_file(), "postgres bundle manifest exists")
    expect(IMPORT_SQL.is_file(), "postgres bundle import.sql exists")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    import_sql = IMPORT_SQL.read_text(encoding="utf-8")

    required_tables = {
        "documents",
        "chunks",
        "canonical_entities",
        "canonical_claims",
        "provenance",
        "search_aliases",
        "build_archetypes",
        "build_core_skills",
        "base_items",
        "runes",
        "runewords",
        "runeword_runes",
        "runeword_item_types",
        "runeword_modifiers",
        "skills",
        "skill_prerequisites",
        "cube_recipes",
        "cube_recipe_inputs",
        "areas",
        "unique_items",
        "monster_resistances",
        "monster_resistance_values",
        "breakpoints",
        "breakpoint_points",
    }
    present_tables = set(manifest.get("tables", {}).keys())
    expect(required_tables.issubset(present_tables), "postgres bundle contains all required tables")

    for table_name, spec in manifest.get("tables", {}).items():
        path = ROOT / spec["path"]
        expect(path.is_file(), f"bundle data file exists: {table_name}")
        with path.open(encoding="utf-8", newline="") as handle:
            row_count = sum(1 for _ in csv.reader(handle, delimiter="\t", quotechar='"'))
        expect(row_count == spec["rows"], f"row count matches manifest for {table_name}")
        expect(f"\\copy d2.{table_name}" in import_sql, f"import.sql loads {table_name}")

    expect(manifest["tables"]["search_aliases"]["rows"] > 2500, "search aliases bundle is substantial")
    expect(manifest["tables"]["canonical_entities"]["rows"] >= 600, "canonical entities bundle is substantial")
    expect(manifest["tables"]["canonical_claims"]["rows"] >= 800, "canonical claims bundle is substantial")
    expect(manifest["tables"]["provenance"]["rows"] >= 900, "provenance bundle is substantial")
    expect(manifest["tables"]["documents"]["rows"] >= 400, "documents bundle is substantial")
    expect(manifest["tables"]["chunks"]["rows"] >= 8000, "chunks bundle is substantial")
    expect(manifest["tables"]["runewords"]["rows"] >= 90, "runewords bundle is substantial")
    expect(manifest["tables"]["breakpoint_points"]["rows"] >= 150, "breakpoint points bundle is substantial")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
