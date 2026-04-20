#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MERGED = ROOT / "docs/tier0/merged"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    manifest = load(MERGED / "manifest.json")
    summary = {
        "base_counts": manifest["base_counts"],
        "high_value_counts": manifest["high_value_counts"],
        "merged_counts": manifest["merged_counts"],
        "paths": manifest["paths"],
    }
    (MERGED / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Merged Graph Summary",
        "",
        f"- Base nodes / edges / claims / chunks: `{summary['base_counts']['nodes']}` / `{summary['base_counts']['edges']}` / `{summary['base_counts']['claims']}` / `{summary['base_counts']['chunks']}`",
        f"- High-value nodes / edges / claims / chunks: `{summary['high_value_counts']['nodes']}` / `{summary['high_value_counts']['edges']}` / `{summary['high_value_counts']['claims']}` / `{summary['high_value_counts']['chunks']}`",
        f"- Merged nodes / edges / claims / chunks: `{summary['merged_counts']['nodes']}` / `{summary['merged_counts']['edges']}` / `{summary['merged_counts']['claims']}` / `{summary['merged_counts']['chunks']}`",
        "",
        "## Outputs",
        "",
        f"- Nodes: `{summary['paths']['nodes']}`",
        f"- Edges: `{summary['paths']['edges']}`",
        f"- Claims: `{summary['paths']['claims']}`",
        f"- Chunks: `{summary['paths']['chunks']}`",
    ]
    (MERGED / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
