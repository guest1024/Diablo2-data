#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.open(encoding="utf-8") if line.strip()]


def main() -> int:
    routing = load_json(ROOT / "docs/tier0/verification/routing-matrix.json")
    curated_docs = load_jsonl(ROOT / "docs/tier0/curated/documents.jsonl")

    groups: dict[str, dict[str, object]] = {}
    for row in curated_docs:
        title = row["metadata"]["title"]
        groups[title] = {
            "title": title,
            "doc_id": row["metadata"]["doc_id"],
            "source": row["metadata"]["source"],
            "keywords": row["metadata"].get("keywords", []),
            "queries": [],
        }

    for row in routing["cases"]:
        if row["lane"] != "curated":
            continue
        title = row["title"]
        if title not in groups:
            groups[title] = {
                "title": title,
                "doc_id": None,
                "source": None,
                "keywords": [],
                "queries": [],
            }
        groups[title]["queries"].append(row["query"])

    ordered = sorted(groups.values(), key=lambda item: item["title"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "curated_cards": len(ordered),
        "cards": ordered,
    }

    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "curated-catalog.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Curated Catalog",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Curated cards: `{report['curated_cards']}`",
        "",
    ]
    for card in ordered:
        lines.append(f"## {card['title']}")
        lines.append("")
        if card["doc_id"]:
            lines.append(f"- doc_id: `{card['doc_id']}`")
        if card["source"]:
            lines.append(f"- source: `{card['source']}`")
        if card["keywords"]:
            lines.append(f"- keywords: `{card['keywords']}`")
        lines.append(f"- routed queries: `{card['queries']}`")
        lines.append("")
    (out_dir / "curated-catalog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"curated_cards": len(ordered)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
