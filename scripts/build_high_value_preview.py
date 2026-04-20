#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> int:
    manifest = load_json(BASE / "manifest.json")
    docs = load_jsonl(BASE / "normalized" / "documents.jsonl")
    docs_by_url = {doc["source_url"]: doc for doc in docs}

    pages = [page for page in manifest["pages"] if page.get("status", "ok") == "ok"]
    pages.sort(key=lambda page: (page.get("chars", 0), page.get("source_id", "")), reverse=True)

    lines = [
        "# High-Value Content Preview",
        "",
        "This file is for quick manual inspection of the highest-value fetched detail pages.",
        "",
    ]
    preview_rows = []
    for idx, page in enumerate(pages[:50], start=1):
        doc = docs_by_url.get(page["url"], {})
        excerpt = (doc.get("text", "") or "").replace("\n", " ").strip()[:600]
        lines += [
            f"## {idx}. {page.get('title','')}",
            "",
            f"- Source: `{page['source_id']}`",
            f"- URL: {page['url']}",
            f"- Chars: `{page.get('chars', 0)}`",
            "",
            excerpt,
            "",
        ]
        preview_rows.append(
            {
                "rank": idx,
                "source_id": page["source_id"],
                "title": page.get("title", ""),
                "url": page["url"],
                "chars": page.get("chars", 0),
                "excerpt": excerpt,
            }
        )

    (BASE / "preview.md").write_text("\n".join(lines), encoding="utf-8")
    (BASE / "preview.json").write_text(json.dumps({"items": preview_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
