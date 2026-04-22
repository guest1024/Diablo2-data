#!/usr/bin/env python3
from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERM_MAP_PATH = ROOT / "docs/tier0/bilingual-term-map.json"
CURATED_DOCS_PATH = ROOT / "docs/tier0/curated/documents.jsonl"
OUT_ALIAS = ROOT / "docs/tier0/alias-registry.jsonl"
OUT_EQ = ROOT / "docs/tier0/term-equivalence.jsonl"
OUT_BUILDS = ROOT / "docs/tier0/build-archetypes.jsonl"


BUILD_TITLES = {
    "Javazon / 标马（Curated Anchor Card）": {
        "build_id": "build::javazon",
        "class": "Amazon",
        "core_skills": ["Lightning Fury", "Charged Strike"],
    },
    "Bowazon / 弓马（Curated Anchor Card）": {
        "build_id": "build::bowazon",
        "class": "Amazon",
        "core_skills": ["Guided Arrow", "Strafe", "Multishot"],
    },
    "Hammerdin / 锤丁（Curated Anchor Card）": {
        "build_id": "build::hammerdin",
        "class": "Paladin",
        "core_skills": ["Blessed Hammer", "Concentration"],
    },
    "Lightning Sorceress / 电法（Curated Anchor Card）": {
        "build_id": "build::lightning-sorceress",
        "class": "Sorceress",
        "core_skills": ["Lightning", "Chain Lightning", "Nova"],
    },
    "Nova Sorceress / 新星电法（Curated Anchor Card）": {
        "build_id": "build::nova-sorceress",
        "class": "Sorceress",
        "core_skills": ["Nova", "Static Field", "Lightning Mastery"],
    },
    "Blizzard Sorceress / 冰法（Curated Anchor Card）": {
        "build_id": "build::blizzard-sorceress",
        "class": "Sorceress",
        "core_skills": ["Blizzard", "Cold Mastery"],
    },
    "Fury Druid / 狼德（Curated Anchor Card）": {
        "build_id": "build::fury-druid",
        "class": "Druid",
        "core_skills": ["Werewolf", "Fury"],
    },
    "Trapsin / 陷阱刺客（Curated Anchor Card）": {
        "build_id": "build::trapsin",
        "class": "Assassin",
        "core_skills": ["Lightning Sentry", "Death Sentry"],
    },
    "Summon Necromancer / 召唤死灵（Curated Anchor Card）": {
        "build_id": "build::summon-necromancer",
        "class": "Necromancer",
        "core_skills": ["Raise Skeleton", "Skeleton Mastery", "Corpse Explosion"],
    },
}


def slugify(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    normalized = lowered.strip("-")
    if normalized:
        return normalized
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
    return f"u-{digest}"


def load_curated_docs() -> list[dict]:
    return [json.loads(line) for line in CURATED_DOCS_PATH.open(encoding="utf-8") if line.strip()]


def main() -> int:
    term_map = json.loads(TERM_MAP_PATH.read_text(encoding="utf-8"))
    curated_docs = load_curated_docs()
    timestamp = datetime.now(timezone.utc).isoformat()

    alias_rows: list[dict] = []
    eq_rows: list[dict] = []

    for term, payload in sorted(term_map.items(), key=lambda item: item[0].lower()):
        canonical_hint = str(payload.get("canonical_hint", "")).strip()
        aliases = [str(alias).strip() for alias in payload.get("aliases", []) if str(alias).strip()]
        canonical_id = f"term::{slugify(canonical_hint or term)}"

        alias_rows.append(
            {
                "alias_id": f"alias::{slugify(term)}::{slugify(canonical_hint or term)}",
                "canonical_id": canonical_id,
                "canonical_name": canonical_hint or term,
                "alias": term,
                "alias_type": "term_map_key",
                "language": "mixed",
                "confidence": 0.99,
                "source": "docs/tier0/bilingual-term-map.json",
                "updated_at": timestamp,
            }
        )

        for idx, alias in enumerate(aliases, start=1):
            language = "zh" if re.search(r"[\u4e00-\u9fff]", alias) else "en"
            alias_rows.append(
                {
                    "alias_id": f"alias::{slugify(alias)}::{idx}",
                    "canonical_id": canonical_id,
                    "canonical_name": canonical_hint or term,
                    "alias": alias,
                    "alias_type": "alias",
                    "language": language,
                    "confidence": 0.95,
                    "source": "docs/tier0/bilingual-term-map.json",
                    "updated_at": timestamp,
                }
            )
            eq_rows.append(
                {
                    "edge_id": f"term-eq::{slugify(term)}::{slugify(alias)}",
                    "lhs": term,
                    "rhs": alias,
                    "canonical_id": canonical_id,
                    "relation": "same_as_term",
                    "confidence": 0.95,
                    "source": "docs/tier0/bilingual-term-map.json",
                    "updated_at": timestamp,
                }
            )

        if canonical_hint:
            eq_rows.append(
                {
                    "edge_id": f"term-eq::{slugify(term)}::{slugify(canonical_hint)}::hint",
                    "lhs": term,
                    "rhs": canonical_hint,
                    "canonical_id": canonical_id,
                    "relation": "canonical_hint",
                    "confidence": 0.99,
                    "source": "docs/tier0/bilingual-term-map.json",
                    "updated_at": timestamp,
                }
            )

    build_rows: list[dict] = []
    curated_by_title = {row["metadata"]["title"]: row for row in curated_docs}
    for title, spec in BUILD_TITLES.items():
        row = curated_by_title.get(title)
        if not row:
            continue
        build_rows.append(
            {
                "build_id": spec["build_id"],
                "canonical_name": title.split(" / ")[0],
                "title": title,
                "class": spec["class"],
                "core_skills": spec["core_skills"],
                "aliases": row["metadata"].get("keywords", []),
                "source": row["metadata"]["source"],
                "source_id": row["metadata"]["source_id"],
                "updated_at": timestamp,
            }
        )

    OUT_ALIAS.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in alias_rows) + "\n", encoding="utf-8")
    OUT_EQ.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in eq_rows) + "\n", encoding="utf-8")
    OUT_BUILDS.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in build_rows) + "\n", encoding="utf-8")

    print(json.dumps({"aliases": len(alias_rows), "equivalences": len(eq_rows), "build_archetypes": len(build_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
