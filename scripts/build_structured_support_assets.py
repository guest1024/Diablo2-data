#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "docs/tier0/raw/blizzhackers-d2data/json-files"
BREAKPOINT_HTML = ROOT / "docs/tier0/raw/diablo2-io/character-info.html"
OUT_DIR = ROOT / "docs/tier0/structured"
MANIFEST_PATH = OUT_DIR / "manifest.json"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_json_if_exists(name: str) -> Any:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(path)
    return load_json(path)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")


def normalize_text(value: str) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return normalized or "unknown"


def resolve_locale(name: str, locale_map: dict[str, str]) -> str:
    if not name:
        return ""
    return str(locale_map.get(name, name)).strip()


def build_base_items(locale_en: dict[str, str], locale_zh: dict[str, str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for dataset_name, bucket in (("armor.json", "armor"), ("weapons.json", "weapon")):
        dataset = load_json_if_exists(dataset_name)
        for code, row in dataset.items():
            name = str(row.get("name") or resolve_locale(str(row.get("namestr", "")), locale_en)).strip()
            zh_name = resolve_locale(str(row.get("namestr", "")), locale_zh)
            rows.append(
                {
                    "item_id": f"base::{code}",
                    "code": code,
                    "name": name,
                    "name_zh": zh_name,
                    "bucket": bucket,
                    "item_type": row.get("type"),
                    "item_type_2": row.get("type2"),
                    "normal_code": row.get("normcode"),
                    "exceptional_code": row.get("ubercode"),
                    "elite_code": row.get("ultracode"),
                    "max_sockets": row.get("gemsockets"),
                    "level": row.get("level"),
                    "level_required": row.get("levelreq"),
                    "required_strength": row.get("reqstr"),
                    "required_dexterity": row.get("reqdex"),
                    "min_armor": row.get("minac"),
                    "max_armor": row.get("maxac"),
                    "min_damage": row.get("mindam"),
                    "max_damage": row.get("maxdam"),
                    "speed": row.get("speed"),
                    "class_specific": bool(row.get("classspecific")),
                    "source": "blizzhackers/d2data",
                    "source_file": dataset_name,
                }
            )
    rows.sort(key=lambda row: (row["bucket"], row["name"], row["code"]))
    return rows


def build_runes(locale_en: dict[str, str], locale_zh: dict[str, str]) -> list[dict[str, Any]]:
    data = load_json_if_exists("misc.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        if row.get("type") != "rune":
            continue
        name = str(row.get("name") or resolve_locale(str(row.get("namestr", "")), locale_en)).strip()
        zh_name = resolve_locale(str(row.get("namestr", "")), locale_zh)
        rows.append(
            {
                "rune_id": f"rune::{slugify(name.replace(' Rune', ''))}",
                "key": key,
                "code": row.get("code") or key,
                "name": name.replace(" Rune", "").strip(),
                "name_zh": zh_name.replace(" 符文", "").strip() if zh_name else zh_name,
                "level": row.get("level"),
                "level_required": row.get("levelreq"),
                "source": "blizzhackers/d2data",
                "source_file": "misc.json",
            }
        )
    rows.sort(key=lambda row: row["level"] or 0)
    return rows


def build_runewords() -> list[dict[str, Any]]:
    data = load_json_if_exists("runes.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        if not row.get("complete"):
            continue
        name = str(row.get("*Rune Name") or key).strip()
        runes_used = [row.get(f"Rune{idx}") for idx in range(1, 7)]
        runes_used = [value for value in runes_used if value not in (None, "")]
        allowed_types = [row.get(f"itype{idx}") for idx in range(1, 7)]
        allowed_types = [value for value in allowed_types if value not in (None, "")]
        modifiers = []
        for idx in range(1, 8):
            code = row.get(f"T1Code{idx}")
            if code in (None, ""):
                continue
            modifiers.append(
                {
                    "code": code,
                    "param": row.get(f"T1Param{idx}"),
                    "min": row.get(f"T1Min{idx}"),
                    "max": row.get(f"T1Max{idx}"),
                }
            )
        rows.append(
            {
                "runeword_id": f"runeword::{slugify(name)}",
                "key": key,
                "name": name,
                "runes_used": runes_used,
                "socket_count": len(runes_used),
                "allowed_item_types": allowed_types,
                "patch_release": row.get("*Patch Release"),
                "modifiers": modifiers,
                "source": "blizzhackers/d2data",
                "source_file": "runes.json",
            }
        )
    rows.sort(key=lambda row: row["name"])
    return rows


def build_unique_items(locale_en: dict[str, str], locale_zh: dict[str, str], base_items_by_code: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    data = load_json_if_exists("uniqueitems.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        raw_name = str(row.get("index") or row.get("name") or row.get("Name", "")).strip()
        name = resolve_locale(raw_name, locale_en) if raw_name else raw_name
        zh_name = resolve_locale(raw_name, locale_zh) if raw_name else ""
        code = str(row.get("code", "")).strip()
        base = base_items_by_code.get(code, {})
        rows.append(
            {
                "unique_item_id": f"unique::{slugify(name or key)}",
                "key": key,
                "name": name,
                "name_zh": zh_name,
                "base_code": code,
                "base_name": base.get("name"),
                "base_name_zh": base.get("name_zh"),
                "rarity": row.get("rarity"),
                "level": row.get("lvl"),
                "level_required": row.get("lvl req"),
                "enabled": row.get("enabled"),
                "cost_multiplier": row.get("cost mult"),
                "cost_add": row.get("cost add"),
                "source": "blizzhackers/d2data",
                "source_file": "uniqueitems.json",
            }
        )
    rows.sort(key=lambda row: row["name"] or row["key"])
    return rows


def build_skills(locale_en: dict[str, str], locale_zh: dict[str, str]) -> list[dict[str, Any]]:
    data = load_json_if_exists("skills.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        raw_name = str(row.get("skill") or row.get("Skill") or row.get("charclass", "")).strip()
        name = resolve_locale(raw_name, locale_en) if raw_name else raw_name
        zh_name = resolve_locale(raw_name, locale_zh) if raw_name else ""
        prereqs = [row.get("reqskill1"), row.get("reqskill2"), row.get("reqskill3")]
        prereqs = [value for value in prereqs if value not in (None, "", 0, "xxx")]
        rows.append(
            {
                "skill_id": f"skill::{slugify(name or key)}",
                "key": key,
                "name": name,
                "name_zh": zh_name,
                "character_class": row.get("charclass"),
                "skill_page": row.get("skillpage"),
                "skill_row": row.get("skillrow"),
                "skill_column": row.get("skillcolumn"),
                "required_level": row.get("reqlevel"),
                "required_skills": prereqs,
                "mana_shift": row.get("manashift"),
                "mana_cost": row.get("mana"),
                "left_skill": row.get("leftskill"),
                "passive": row.get("passive"),
                "source": "blizzhackers/d2data",
                "source_file": "skills.json",
            }
        )
    rows.sort(key=lambda row: ((row.get("character_class") or ""), row["name"] or row["key"]))
    return rows


def classify_cube_recipe(description: str, output: str) -> str:
    desc = description.lower()
    if "upgrade" in desc or output.startswith("usetype"):
        return "upgrade"
    if "socket" in desc or "sock" in desc:
        return "socket"
    if "repair" in desc:
        return "repair"
    if "crafted" in desc:
        return "crafted"
    if "rune" in desc and "->" in description:
        return "rune_upgrade"
    if "reroll" in desc or "random" in desc or "rejuv" in desc:
        return "reroll_or_transform"
    return "other"


def build_cube_recipes() -> list[dict[str, Any]]:
    data = load_json_if_exists("cubemain.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        inputs = []
        for idx in range(1, 8):
            value = row.get(f"input {idx}")
            if value not in (None, ""):
                inputs.append(value)
        description = str(row.get("description", "")).strip()
        output = str(row.get("output", "")).strip()
        rows.append(
            {
                "recipe_id": f"cube::{key}",
                "row_id": key,
                "description": description,
                "recipe_type": classify_cube_recipe(description, output),
                "enabled": row.get("enabled"),
                "version": row.get("version"),
                "num_inputs": row.get("numinputs"),
                "inputs": inputs,
                "output": output,
                "modifiers": {k: v for k, v in row.items() if k.startswith("mod ") or k.startswith("param ") or k.startswith("value ")},
                "source": "blizzhackers/d2data",
                "source_file": "cubemain.json",
            }
        )
    rows.sort(key=lambda row: int(row["row_id"]) if str(row["row_id"]).isdigit() else row["row_id"])
    return rows


def build_areas(locale_en: dict[str, str], locale_zh: dict[str, str]) -> list[dict[str, Any]]:
    data = load_json_if_exists("levels.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        name_key = str(row.get("LevelName") or row.get("Name") or row.get("NameStr") or "").strip()
        name = resolve_locale(name_key, locale_en)
        zh_name = resolve_locale(name_key, locale_zh)
        if not name or name.lower() in {"dummy", "expansion", "guildhall", "random level"}:
            continue
        rows.append(
            {
                "area_id": f"area::{slugify(name)}::{row.get('Id', key)}",
                "row_id": key,
                "id": row.get("Id"),
                "name": name,
                "name_zh": zh_name,
                "act": row.get("Act"),
                "is_inside": row.get("*IsInside"),
                "is_town": row.get("Town"),
                "level_normal": row.get("MonLvl"),
                "level_nightmare": row.get("MonLvl(N)"),
                "level_hell": row.get("MonLvl(H)"),
                "monster_density_normal": row.get("MonDen"),
                "monster_density_nightmare": row.get("MonDen(N)"),
                "monster_density_hell": row.get("MonDen(H)"),
                "waypoint": row.get("Waypoint"),
                "quest": row.get("Quest"),
                "source": "blizzhackers/d2data",
                "source_file": "levels.json",
            }
        )
    rows.sort(key=lambda row: (row.get("act") or 0, row["name"]))
    return rows


def build_monster_resistances(locale_en: dict[str, str], locale_zh: dict[str, str]) -> list[dict[str, Any]]:
    data = load_json_if_exists("monstats.json")
    rows: list[dict[str, Any]] = []
    for key, row in data.items():
        name_key = str(row.get("NameStr") or row.get("Id") or key).strip()
        name = resolve_locale(name_key, locale_en)
        zh_name = resolve_locale(name_key, locale_zh)
        if not name or name.lower() == "dummy":
            continue
        def diff(prefix: str) -> dict[str, Any]:
            return {
                "normal": row.get(prefix),
                "nightmare": row.get(f"{prefix}(N)"),
                "hell": row.get(f"{prefix}(H)"),
            }
        resistances = {
            "physical": diff("ResDm"),
            "magic": diff("ResMa"),
            "fire": diff("ResFi"),
            "lightning": diff("ResLi"),
            "cold": diff("ResCo"),
            "poison": diff("ResPo"),
            "drain_effectiveness": diff("Drain"),
        }
        has_data = any(any(value not in (None, "") for value in bucket.values()) for bucket in resistances.values())
        if not has_data:
            continue
        rows.append(
            {
                "monster_id": f"monster::{slugify(name)}::{key}",
                "key": key,
                "name": name,
                "name_zh": zh_name,
                "monster_type": row.get("MonType"),
                "base_id": row.get("BaseId"),
                "enabled": row.get("enabled"),
                "resistances": resistances,
                "source": "blizzhackers/d2data",
                "source_file": "monstats.json",
            }
        )
    rows.sort(key=lambda row: row["name"])
    return rows


def extract_breakpoint_section(html_text: str, title: str) -> str:
    pattern = re.compile(rf"<details class=\"spoiler\"><summary[^>]*>.*?{re.escape(title)}.*?</summary><div class=\"spoiler-body\">(.*?)</div></details>", re.S)
    match = pattern.search(html_text)
    if not match:
        raise ValueError(f"unable to locate breakpoint section: {title}")
    return match.group(1)


def parse_breakpoint_section(html_text: str, category: str) -> list[dict[str, Any]]:
    section = extract_breakpoint_section(html_text, category)
    parts = re.split(r'<strong class="text-strong">', section)[1:]
    rows: list[dict[str, Any]] = []
    for part in parts:
        name_html, rest = part.split("</strong>", 1)
        name = normalize_text(name_html)
        block = normalize_text(rest)
        values: list[dict[str, int]] = []
        for pct, frames in re.findall(r"(\d+)%\s*-+\s*(\d+)", block):
            values.append({"value": int(pct), "frames": int(frames)})
        if not values:
            continue
        rows.append(
            {
                "breakpoint_id": f"{category.lower()}::{slugify(name)}",
                "category": category,
                "entity": name,
                "breakpoints": values,
                "source": "diablo2.io",
                "source_url": "https://diablo2.io/forums/character-info-t850955.html",
            }
        )
    rows.sort(key=lambda row: row["entity"])
    return rows


def build_breakpoints() -> list[dict[str, Any]]:
    html_text = BREAKPOINT_HTML.read_text(encoding="utf-8")
    rows: list[dict[str, Any]] = []
    for category in ("Faster Cast Rate (FCR)", "Faster Hit Recovery (FHR)", "Faster Block Rate (FBR)"):
        short = re.search(r"\(([^)]+)\)", category).group(1)
        rows.extend(parse_breakpoint_section(html_text, category=short))
    return rows


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    locale_en = load_json_if_exists("localestrings-eng.json")
    locale_zh = load_json_if_exists("localestrings-chi.json")

    base_items = build_base_items(locale_en, locale_zh)
    base_items_by_code = {row["code"]: row for row in base_items}
    runes = build_runes(locale_en, locale_zh)
    runewords = build_runewords()
    unique_items = build_unique_items(locale_en, locale_zh, base_items_by_code)
    skills = build_skills(locale_en, locale_zh)
    cube_recipes = build_cube_recipes()
    areas = build_areas(locale_en, locale_zh)
    monster_resistances = build_monster_resistances(locale_en, locale_zh)
    breakpoints = build_breakpoints()

    outputs = {
        "base-items.jsonl": base_items,
        "runes.jsonl": runes,
        "runewords.jsonl": runewords,
        "unique-items.jsonl": unique_items,
        "skills.jsonl": skills,
        "cube-recipes.jsonl": cube_recipes,
        "areas.jsonl": areas,
        "monster-resistances.jsonl": monster_resistances,
        "breakpoints.jsonl": breakpoints,
    }
    for name, rows in outputs.items():
        write_jsonl(OUT_DIR / name, rows)

    manifest = {
        "outputs": {name: len(rows) for name, rows in outputs.items()},
        "sources": {
            "blizzhackers_manifest": "docs/tier0/raw/blizzhackers-d2data/structured-subset-manifest.json",
            "breakpoint_reference": "docs/tier0/raw/diablo2-io/character-info.html",
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["outputs"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
