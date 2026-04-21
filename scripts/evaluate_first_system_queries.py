#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


REQUIRED_CASES = [
    {"query": "Spirit 是什么？", "keywords": ["spirit"]},
    {"query": "军帽是什么？", "keywords": ["harlequin crest", "shako"]},
    {"query": "精神符文之语是什么？", "keywords": ["spirit"]},
    {"query": "What is Hellfire Torch?", "keywords": ["hellfire torch"]},
    {"query": "火炬是什么？", "keywords": ["hellfire torch"]},
    {"query": "地狱火炬是什么？", "keywords": ["hellfire torch"]},
    {"query": "谜团是什么？", "keywords": ["enigma"]},
]

EXPLORATORY_CASES = [
    {"query": "超市是什么？", "keywords": ["chaos sanctuary"]},
    {"query": "古代通道是什么？", "keywords": ["ancient tunnels"]},
    {"query": "劳模是什么？", "keywords": ["mephisto"]},
    {"query": "女伯爵是什么？", "keywords": ["countess"]},
    {"query": "乔丹是什么？", "keywords": ["stone of jordan"]},
    {"query": "无限是什么？", "keywords": ["infinity"]},
    {"query": "大菠萝是什么？", "keywords": ["diablo"]},
]


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def evaluate_case(service: Diablo2QAService, case: dict[str, object]) -> dict[str, object]:
    query = str(case["query"])
    keywords = [normalize(str(keyword)) for keyword in case.get("keywords", [])]
    body = service.answer(query, use_llm=False)
    top_chunk = (body.get("chunks") or [{}])[0]
    top_title = str(top_chunk.get("metadata", {}).get("title", ""))
    top_text = str(top_chunk.get("text", ""))
    haystack = normalize(f"{top_title}\n{top_text[:600]}")
    matched_keywords = [keyword for keyword in keywords if keyword in haystack]
    return {
        "query": query,
        "matched_keywords": matched_keywords,
        "passed": bool(matched_keywords),
        "resolved_entities": len(body.get("resolved_entities", [])),
        "confident_entity_ids": body.get("confident_entity_ids", []),
        "top_chunk_source": top_chunk.get("retrieval_source"),
        "top_chunk_title": top_title,
        "top_chunk_preview": top_text[:240],
        "query_context": body.get("query_context", {}),
    }


def write_report(report: dict[str, object]) -> None:
    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "first-system-query-eval.json"
    md_path = out_dir / "first-system-query-eval.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# First System Query Evaluation",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Required pass count: `{report['required_summary']['passed']}/{report['required_summary']['total']}`",
        f"- Exploratory pass count: `{report['exploratory_summary']['passed']}/{report['exploratory_summary']['total']}`",
        "- Note: exploratory cases use keyword-hit heuristics and still require manual review.",
        "",
        "## Required cases",
        "",
    ]
    for row in report["required_cases"]:
        status = "PASS" if row["passed"] else "FAIL"
        lines.extend(
            [
                f"### [{status}] {row['query']}",
                f"- top_chunk_source: `{row['top_chunk_source']}`",
                f"- top_chunk_title: `{row['top_chunk_title']}`",
                f"- matched_keywords: `{row['matched_keywords']}`",
                "",
            ]
        )
    lines.extend(["## Exploratory cases", ""])
    for row in report["exploratory_cases"]:
        status = "PASS" if row["passed"] else "GAP"
        lines.extend(
            [
                f"### [{status}] {row['query']}",
                f"- top_chunk_source: `{row['top_chunk_source']}`",
                f"- top_chunk_title: `{row['top_chunk_title']}`",
                f"- matched_keywords: `{row['matched_keywords']}`",
                "",
            ]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    service = Diablo2QAService()
    service.ingest()

    required_rows = [evaluate_case(service, case) for case in REQUIRED_CASES]
    exploratory_rows = [evaluate_case(service, case) for case in EXPLORATORY_CASES]

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "required_summary": {
            "passed": sum(1 for row in required_rows if row["passed"]),
            "total": len(required_rows),
        },
        "exploratory_summary": {
            "passed": sum(1 for row in exploratory_rows if row["passed"]),
            "total": len(exploratory_rows),
        },
        "required_cases": required_rows,
        "exploratory_cases": exploratory_rows,
    }
    write_report(report)
    print(json.dumps(report["required_summary"], ensure_ascii=False))
    print(json.dumps(report["exploratory_summary"], ensure_ascii=False))
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
