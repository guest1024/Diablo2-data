#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_DIR = ROOT / "docs/tier0/postgres-bundle"
DATA_DIR = BUNDLE_DIR / "data"
MANIFEST_PATH = BUNDLE_DIR / "manifest.json"
IMPORT_SQL_PATH = BUNDLE_DIR / "import.sql"

MERGED_DOCS = ROOT / "docs/tier0/merged/normalized/documents.jsonl"
MERGED_CHUNKS = ROOT / "docs/tier0/merged/chunks.jsonl"
MERGED_ALIASES = ROOT / "docs/tier0/merged/aliases.jsonl"
MERGED_ENTITIES = ROOT / "docs/tier0/merged/canonical-entities.jsonl"
ALIAS_REGISTRY = ROOT / "docs/tier0/alias-registry.jsonl"
BUILD_ARCHETYPES = ROOT / "docs/tier0/build-archetypes.jsonl"
STRUCTURED_DIR = ROOT / "docs/tier0/structured"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_tsv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", quotechar='"', lineterminator="\n")
        for row in rows:
            writer.writerow(["\\N" if row.get(col) is None else row.get(col) for col in columns])


def ordered_metadata(row: dict[str, Any], known_keys: set[str]) -> str:
    return json_dumps({key: row[key] for key in row.keys() if key not in known_keys})


def build_documents() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(MERGED_DOCS):
        known = {
            "doc_id", "source_id", "source_name", "label", "source_url", "local_path", "content_type",
            "authority_tier", "lane", "title", "text", "char_count",
        }
        rows.append(
            {
                "doc_id": row["doc_id"],
                "source_id": row["source_id"],
                "source_name": row.get("source_name"),
                "label": row.get("label"),
                "source_url": row["source_url"],
                "local_path": row.get("local_path"),
                "content_type": row.get("content_type"),
                "authority_tier": row.get("authority_tier"),
                "lane": row.get("lane"),
                "title": row["title"],
                "text_content": row["text"],
                "char_count": row.get("char_count"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = [
        "doc_id", "source_id", "source_name", "label", "source_url", "local_path", "content_type",
        "authority_tier", "lane", "title", "text_content", "char_count", "metadata",
    ]
    return rows, columns


def build_chunks() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(MERGED_CHUNKS):
        known = {
            "chunk_id", "doc_id", "source_id", "source_name", "source_url", "label", "title", "lane",
            "authority_tier", "chunk_index", "text", "char_count",
        }
        rows.append(
            {
                "chunk_id": row["chunk_id"],
                "doc_id": row["doc_id"],
                "source_id": row["source_id"],
                "source_name": row.get("source_name"),
                "source_url": row.get("source_url"),
                "label": row.get("label"),
                "title": row.get("title"),
                "lane": row.get("lane"),
                "authority_tier": row.get("authority_tier"),
                "chunk_index": row.get("chunk_index"),
                "text_content": row["text"],
                "char_count": row.get("char_count"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = [
        "chunk_id", "doc_id", "source_id", "source_name", "source_url", "label", "title", "lane",
        "authority_tier", "chunk_index", "text_content", "char_count", "metadata",
    ]
    return rows, columns


def build_search_aliases() -> tuple[list[dict[str, Any]], list[str]]:
    merged_entities = {row["canonical_id"]: row for row in load_jsonl(MERGED_ENTITIES)}
    rows_map: OrderedDict[str, dict[str, Any]] = OrderedDict()

    for row in load_jsonl(ALIAS_REGISTRY):
        rows_map[row["alias_id"]] = {
            "alias_id": row["alias_id"],
            "canonical_id": row["canonical_id"],
            "canonical_name": row.get("canonical_name"),
            "alias": row["alias"],
            "alias_type": row.get("alias_type"),
            "node_type": row.get("node_type") or "TermAlias",
            "language": row.get("language"),
            "confidence": row.get("confidence"),
            "source": row.get("source"),
            "metadata": json_dumps({
                "source_scope": "alias_registry",
                "updated_at": row.get("updated_at"),
            }),
        }

    for row in load_jsonl(MERGED_ALIASES):
        entity = merged_entities.get(row["canonical_id"], {})
        alias_id = f"merged::{row['alias_id']}"
        rows_map[alias_id] = {
            "alias_id": alias_id,
            "canonical_id": row["canonical_id"],
            "canonical_name": entity.get("name"),
            "alias": row["alias"],
            "alias_type": row.get("alias_type"),
            "node_type": row.get("node_type") or entity.get("node_type"),
            "language": None,
            "confidence": None,
            "source": "docs/tier0/merged/aliases.jsonl",
            "metadata": json_dumps({"source_scope": "merged_aliases"}),
        }

    rows = list(rows_map.values())
    columns = [
        "alias_id", "canonical_id", "canonical_name", "alias", "alias_type", "node_type", "language",
        "confidence", "source", "metadata",
    ]
    return rows, columns


def build_builds() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    builds_rows = []
    skill_rows = []
    for row in load_jsonl(BUILD_ARCHETYPES):
        builds_rows.append(
            {
                "build_id": row["build_id"],
                "canonical_name": row["canonical_name"],
                "title": row.get("title"),
                "class_name": row.get("class"),
                "source": row.get("source"),
                "source_id": row.get("source_id"),
                "aliases": json_dumps(row.get("aliases", [])),
                "metadata": json_dumps({"updated_at": row.get("updated_at")}),
            }
        )
        for idx, skill in enumerate(row.get("core_skills", []), start=1):
            skill_rows.append(
                {
                    "build_id": row["build_id"],
                    "skill_name": skill,
                    "skill_order": idx,
                }
            )
    return {
        "build_archetypes": (builds_rows, ["build_id", "canonical_name", "title", "class_name", "source", "source_id", "aliases", "metadata"]),
        "build_core_skills": (skill_rows, ["build_id", "skill_name", "skill_order"]),
    }


def build_base_items() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(STRUCTURED_DIR / "base-items.jsonl"):
        known = {
            "item_id", "code", "name", "name_zh", "bucket", "item_type", "item_type_2", "normal_code",
            "exceptional_code", "elite_code", "max_sockets", "level", "level_required", "required_strength",
            "required_dexterity", "min_armor", "max_armor", "min_damage", "max_damage", "speed",
            "class_specific", "source", "source_file",
        }
        rows.append(
            {
                "item_id": row["item_id"],
                "code": row["code"],
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "bucket": row.get("bucket"),
                "item_type": row.get("item_type"),
                "item_type_2": row.get("item_type_2"),
                "normal_code": row.get("normal_code"),
                "exceptional_code": row.get("exceptional_code"),
                "elite_code": row.get("elite_code"),
                "max_sockets": row.get("max_sockets"),
                "level": row.get("level"),
                "level_required": row.get("level_required"),
                "required_strength": row.get("required_strength"),
                "required_dexterity": row.get("required_dexterity"),
                "min_armor": row.get("min_armor"),
                "max_armor": row.get("max_armor"),
                "min_damage": row.get("min_damage"),
                "max_damage": row.get("max_damage"),
                "speed": row.get("speed"),
                "class_specific": row.get("class_specific"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = [
        "item_id", "code", "name", "name_zh", "bucket", "item_type", "item_type_2", "normal_code",
        "exceptional_code", "elite_code", "max_sockets", "level", "level_required", "required_strength",
        "required_dexterity", "min_armor", "max_armor", "min_damage", "max_damage", "speed",
        "class_specific", "source", "source_file", "metadata",
    ]
    return rows, columns


def build_runes() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(STRUCTURED_DIR / "runes.jsonl"):
        known = {"rune_id", "key", "code", "name", "name_zh", "level", "level_required", "source", "source_file"}
        rows.append(
            {
                "rune_id": row["rune_id"],
                "rune_key": row["key"],
                "code": row["code"],
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "level": row.get("level"),
                "level_required": row.get("level_required"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = ["rune_id", "rune_key", "code", "name", "name_zh", "level", "level_required", "source", "source_file", "metadata"]
    return rows, columns


def build_runewords() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    runewords_rows = []
    rune_rows = []
    item_type_rows = []
    modifier_rows = []
    for row in load_jsonl(STRUCTURED_DIR / "runewords.jsonl"):
        known = {"runeword_id", "key", "name", "runes_used", "socket_count", "allowed_item_types", "patch_release", "modifiers", "source", "source_file"}
        runewords_rows.append(
            {
                "runeword_id": row["runeword_id"],
                "runeword_key": row.get("key"),
                "name": row["name"],
                "socket_count": row["socket_count"],
                "patch_release": str(row.get("patch_release")) if row.get("patch_release") is not None else None,
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
        for idx, rune_code in enumerate(row.get("runes_used", []), start=1):
            rune_rows.append({"runeword_id": row["runeword_id"], "rune_order": idx, "rune_code": rune_code})
        for item_type in row.get("allowed_item_types", []):
            item_type_rows.append({"runeword_id": row["runeword_id"], "item_type_code": item_type})
        for idx, modifier in enumerate(row.get("modifiers", []), start=1):
            modifier_rows.append(
                {
                    "runeword_id": row["runeword_id"],
                    "modifier_order": idx,
                    "modifier_code": modifier.get("code"),
                    "modifier_param": modifier.get("param"),
                    "min_value": modifier.get("min"),
                    "max_value": modifier.get("max"),
                }
            )
    return {
        "runewords": (runewords_rows, ["runeword_id", "runeword_key", "name", "socket_count", "patch_release", "source", "source_file", "metadata"]),
        "runeword_runes": (rune_rows, ["runeword_id", "rune_order", "rune_code"]),
        "runeword_item_types": (item_type_rows, ["runeword_id", "item_type_code"]),
        "runeword_modifiers": (modifier_rows, ["runeword_id", "modifier_order", "modifier_code", "modifier_param", "min_value", "max_value"]),
    }


def build_skills() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    skills_rows = []
    prereq_rows = []
    skill_name_to_id: dict[str, str] = {}
    source_rows = [row for row in load_jsonl(STRUCTURED_DIR / "skills.jsonl") if row.get("name")]
    for row in source_rows:
        known = {"skill_id", "key", "name", "name_zh", "character_class", "skill_page", "skill_row", "skill_column", "required_level", "required_skills", "mana_shift", "mana_cost", "left_skill", "passive", "source", "source_file"}
        skills_rows.append(
            {
                "skill_id": row["skill_id"],
                "skill_key": row.get("key"),
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "character_class": row.get("character_class"),
                "skill_page": row.get("skill_page"),
                "skill_row": row.get("skill_row"),
                "skill_column": row.get("skill_column"),
                "required_level": row.get("required_level"),
                "mana_shift": row.get("mana_shift"),
                "mana_cost": row.get("mana_cost"),
                "left_skill": row.get("left_skill"),
                "passive": row.get("passive"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
        skill_name_to_id[row["name"].lower()] = row["skill_id"]
    for row in source_rows:
        for idx, prereq in enumerate(row.get("required_skills", []), start=1):
            prereq_rows.append(
                {
                    "skill_id": row["skill_id"],
                    "prerequisite_order": idx,
                    "prerequisite_name": prereq,
                    "prerequisite_skill_id": skill_name_to_id.get(prereq.lower()),
                }
            )
    return {
        "skills": (skills_rows, ["skill_id", "skill_key", "name", "name_zh", "character_class", "skill_page", "skill_row", "skill_column", "required_level", "mana_shift", "mana_cost", "left_skill", "passive", "source", "source_file", "metadata"]),
        "skill_prerequisites": (prereq_rows, ["skill_id", "prerequisite_order", "prerequisite_name", "prerequisite_skill_id"]),
    }


def build_cube_recipes() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    recipe_rows = []
    input_rows = []
    for row in load_jsonl(STRUCTURED_DIR / "cube-recipes.jsonl"):
        known = {"recipe_id", "row_id", "description", "recipe_type", "enabled", "version", "num_inputs", "inputs", "output", "modifiers", "source", "source_file"}
        recipe_rows.append(
            {
                "recipe_id": row["recipe_id"],
                "row_id": row.get("row_id"),
                "description": row["description"],
                "recipe_type": row.get("recipe_type"),
                "enabled": row.get("enabled"),
                "version": str(row.get("version")) if row.get("version") is not None else None,
                "num_inputs": row.get("num_inputs"),
                "output_code": row.get("output"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "modifiers": json_dumps(row.get("modifiers", {})),
                "metadata": ordered_metadata(row, known),
            }
        )
        for idx, input_code in enumerate(row.get("inputs", []), start=1):
            input_rows.append({"recipe_id": row["recipe_id"], "input_order": idx, "input_code": input_code})
    return {
        "cube_recipes": (recipe_rows, ["recipe_id", "row_id", "description", "recipe_type", "enabled", "version", "num_inputs", "output_code", "source", "source_file", "modifiers", "metadata"]),
        "cube_recipe_inputs": (input_rows, ["recipe_id", "input_order", "input_code"]),
    }


def build_areas() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(STRUCTURED_DIR / "areas.jsonl"):
        known = {"area_id", "row_id", "id", "name", "name_zh", "act", "is_inside", "is_town", "level_normal", "level_nightmare", "level_hell", "monster_density_normal", "monster_density_nightmare", "monster_density_hell", "waypoint", "quest", "source", "source_file"}
        rows.append(
            {
                "area_id": row["area_id"],
                "row_id": row.get("row_id"),
                "level_id": row.get("id"),
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "act": row.get("act"),
                "is_inside": row.get("is_inside"),
                "is_town": row.get("is_town"),
                "level_normal": row.get("level_normal"),
                "level_nightmare": row.get("level_nightmare"),
                "level_hell": row.get("level_hell"),
                "monster_density_normal": row.get("monster_density_normal"),
                "monster_density_nightmare": row.get("monster_density_nightmare"),
                "monster_density_hell": row.get("monster_density_hell"),
                "waypoint": row.get("waypoint"),
                "quest": row.get("quest"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = [
        "area_id", "row_id", "level_id", "name", "name_zh", "act", "is_inside", "is_town", "level_normal",
        "level_nightmare", "level_hell", "monster_density_normal", "monster_density_nightmare", "monster_density_hell",
        "waypoint", "quest", "source", "source_file", "metadata",
    ]
    return rows, columns


def build_unique_items() -> tuple[list[dict[str, Any]], list[str]]:
    rows = []
    for row in load_jsonl(STRUCTURED_DIR / "unique-items.jsonl"):
        known = {"unique_item_id", "key", "name", "name_zh", "base_code", "base_name", "base_name_zh", "rarity", "level", "level_required", "enabled", "cost_multiplier", "cost_add", "source", "source_file"}
        rows.append(
            {
                "unique_item_id": row["unique_item_id"],
                "unique_key": row.get("key"),
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "base_code": row.get("base_code"),
                "base_name": row.get("base_name"),
                "base_name_zh": row.get("base_name_zh"),
                "rarity": row.get("rarity"),
                "level": row.get("level"),
                "level_required": row.get("level_required"),
                "enabled": row.get("enabled"),
                "cost_multiplier": row.get("cost_multiplier"),
                "cost_add": row.get("cost_add"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
    columns = ["unique_item_id", "unique_key", "name", "name_zh", "base_code", "base_name", "base_name_zh", "rarity", "level", "level_required", "enabled", "cost_multiplier", "cost_add", "source", "source_file", "metadata"]
    return rows, columns


def build_monsters() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    monster_rows = []
    resistance_rows = []
    for row in load_jsonl(STRUCTURED_DIR / "monster-resistances.jsonl"):
        known = {"monster_id", "key", "name", "name_zh", "monster_type", "base_id", "enabled", "resistances", "source", "source_file"}
        monster_rows.append(
            {
                "monster_id": row["monster_id"],
                "monster_key": row.get("key"),
                "name": row["name"],
                "name_zh": row.get("name_zh"),
                "monster_type": row.get("monster_type"),
                "base_id": row.get("base_id"),
                "enabled": row.get("enabled"),
                "source": row.get("source"),
                "source_file": row.get("source_file"),
                "metadata": ordered_metadata(row, known),
            }
        )
        for resistance_type, values in row.get("resistances", {}).items():
            resistance_rows.append(
                {
                    "monster_id": row["monster_id"],
                    "resistance_type": resistance_type,
                    "normal_value": values.get("normal"),
                    "nightmare_value": values.get("nightmare"),
                    "hell_value": values.get("hell"),
                }
            )
    return {
        "monster_resistances": (monster_rows, ["monster_id", "monster_key", "name", "name_zh", "monster_type", "base_id", "enabled", "source", "source_file", "metadata"]),
        "monster_resistance_values": (resistance_rows, ["monster_id", "resistance_type", "normal_value", "nightmare_value", "hell_value"]),
    }


def build_breakpoints() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    breakpoint_rows = []
    point_rows = []
    for row in load_jsonl(STRUCTURED_DIR / "breakpoints.jsonl"):
        known = {"breakpoint_id", "category", "entity", "breakpoints", "source", "source_url"}
        breakpoint_rows.append(
            {
                "breakpoint_id": row["breakpoint_id"],
                "category": row["category"],
                "entity_name": row["entity"],
                "source": row.get("source"),
                "source_url": row.get("source_url"),
                "metadata": ordered_metadata(row, known),
            }
        )
        for idx, point in enumerate(row.get("breakpoints", []), start=1):
            point_rows.append(
                {
                    "breakpoint_id": row["breakpoint_id"],
                    "point_order": idx,
                    "breakpoint_value": point.get("value"),
                    "frames": point.get("frames"),
                }
            )
    return {
        "breakpoints": (breakpoint_rows, ["breakpoint_id", "category", "entity_name", "source", "source_url", "metadata"]),
        "breakpoint_points": (point_rows, ["breakpoint_id", "point_order", "breakpoint_value", "frames"]),
    }


def build_import_sql(table_specs: dict[str, tuple[list[dict[str, Any]], list[str]]]) -> str:
    load_order = [
        "documents",
        "chunks",
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
    ]
    reverse_delete = list(reversed(load_order))
    lines = [
        "\\set ON_ERROR_STOP on",
        "BEGIN;",
    ]
    for table_name in reverse_delete:
        lines.append(f"TRUNCATE TABLE d2.{table_name} CASCADE;")
    for table_name in load_order:
        _, columns = table_specs[table_name]
        data_path = (DATA_DIR / f"{table_name}.tsv").resolve()
        quoted_columns = ", ".join(columns)
        lines.append(
            f"\\copy d2.{table_name} ({quoted_columns}) FROM '{data_path}' WITH (FORMAT csv, DELIMITER E'\\t', QUOTE '\"', NULL '\\N')"
        )
    lines.append("COMMIT;")
    return "\n".join(lines) + "\n"


def main() -> int:
    table_specs: dict[str, tuple[list[dict[str, Any]], list[str]]] = {}
    table_specs["documents"] = build_documents()
    table_specs["chunks"] = build_chunks()
    table_specs["search_aliases"] = build_search_aliases()
    table_specs.update(build_builds())
    table_specs["base_items"] = build_base_items()
    table_specs["runes"] = build_runes()
    table_specs.update(build_runewords())
    table_specs.update(build_skills())
    table_specs.update(build_cube_recipes())
    table_specs["areas"] = build_areas()
    table_specs["unique_items"] = build_unique_items()
    table_specs.update(build_monsters())
    table_specs.update(build_breakpoints())

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    manifest_tables = {}
    for table_name, (rows, columns) in table_specs.items():
        write_tsv(DATA_DIR / f"{table_name}.tsv", rows, columns)
        manifest_tables[table_name] = {
            "rows": len(rows),
            "columns": columns,
            "path": str((DATA_DIR / f"{table_name}.tsv").relative_to(ROOT)),
        }

    IMPORT_SQL_PATH.write_text(build_import_sql(table_specs), encoding="utf-8")
    manifest = {
        "schema_files": [
            "sql/postgres/001_core_schema.sql",
            "sql/postgres/002_optional_vector.sql",
            "sql/postgres/003_views.sql",
            "sql/postgres/queries.sql",
        ],
        "tables": manifest_tables,
        "import_sql": str(IMPORT_SQL_PATH.relative_to(ROOT)),
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({table: spec["rows"] for table, spec in manifest_tables.items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
