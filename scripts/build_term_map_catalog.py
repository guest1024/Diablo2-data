#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    term_map = json.loads((ROOT / "docs/tier0/bilingual-term-map.json").read_text(encoding="utf-8"))

    rows = []
    for term, payload in sorted(term_map.items(), key=lambda item: item[0].lower()):
        rows.append(
            {
                "term": term,
                "canonical_hint": payload.get("canonical_hint", ""),
                "aliases": payload.get("aliases", []),
                "preferred_source_ids": payload.get("preferred_source_ids", []),
                "preferred_title_contains": payload.get("preferred_title_contains", []),
                "preferred_text_contains": payload.get("preferred_text_contains", []),
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entries": len(rows),
        "rows": rows,
    }

    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "term-map-catalog.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Term Map Catalog",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Entries: `{report['entries']}`",
        "",
    ]
    for row in rows:
        lines.append(f"## {row['term']}")
        lines.append("")
        lines.append(f"- canonical_hint: `{row['canonical_hint']}`")
        lines.append(f"- aliases: `{row['aliases']}`")
        if row["preferred_source_ids"]:
            lines.append(f"- preferred_source_ids: `{row['preferred_source_ids']}`")
        if row["preferred_title_contains"]:
            lines.append(f"- preferred_title_contains: `{row['preferred_title_contains']}`")
        if row["preferred_text_contains"]:
            lines.append(f"- preferred_text_contains: `{row['preferred_text_contains']}`")
        lines.append("")
    (out_dir / "term-map-catalog.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"entries": len(rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
