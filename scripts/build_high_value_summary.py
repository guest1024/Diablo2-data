#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/tier0/high-value"


def main() -> int:
    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    errors = sum(1 for page in manifest["pages"] if page.get("status") == "error")
    summary = {
        "page_count": manifest["page_count"],
        "chunk_count": manifest["chunk_count"],
        "error_count": errors,
        "successful_page_count": manifest["page_count"] - errors,
        "sources": manifest["sources"],
        "documents_path": manifest["documents_path"],
        "chunks_path": manifest["chunks_path"],
    }
    (BASE / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# High-Value Corpus Summary",
        "",
        f"- Pages fetched: `{summary['page_count']}`",
        f"- Successful pages: `{summary['successful_page_count']}`",
        f"- Error pages: `{summary['error_count']}`",
        f"- Chunks generated: `{summary['chunk_count']}`",
        "",
        "## By source",
        "",
        "| Source | Pages | Chars | Chunks |",
        "| --- | ---: | ---: | ---: |",
    ]
    for source, stats in sorted(summary["sources"].items()):
        lines.append(f"| {source} | {stats['pages']} | {stats['chars']} | {stats['chunks']} |")
    lines += [
        "",
        "## Main outputs",
        "",
        f"- Documents: `{summary['documents_path']}`",
        f"- Chunks: `{summary['chunks_path']}`",
        f"- Manifest: `docs/tier0/high-value/manifest.json`",
        f"- Report: `docs/tier0/high-value/report.md`",
    ]
    (BASE / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
