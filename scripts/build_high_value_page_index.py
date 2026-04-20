#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value"


def main() -> int:
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    pages = [page for page in manifest["pages"] if page.get("status", "ok") == "ok"]
    pages.sort(key=lambda page: (page.get("chars", 0), page.get("source_id", "")), reverse=True)
    payload = {
        "total_pages": len(manifest["pages"]),
        "successful_pages": len(pages),
        "error_pages": sum(1 for page in manifest["pages"] if page.get("status") == "error"),
        "top_pages": pages[:100],
    }
    (BASE / "page-index.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# High-Value Page Index",
        "",
        f"- Total pages: `{payload['total_pages']}`",
        f"- Successful pages: `{payload['successful_pages']}`",
        f"- Error pages: `{payload['error_pages']}`",
        "",
        "| Source | Chars | Title | URL |",
        "| --- | ---: | --- | --- |",
    ]
    for page in pages[:100]:
        title = (page.get("title", "") or "").replace("\n", " ").strip()
        lines.append(f"| {page['source_id']} | {page.get('chars', 0)} | {title[:100]} | {page['url']} |")
    (BASE / "page-index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
