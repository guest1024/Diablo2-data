#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


RETRIEVAL_CASES = [
    {"category": "alias_fact", "query": "劳模掉不掉军帽？", "expected_keywords": ["mephisto", "劳模", "军帽", "harlequin"]},
    {"category": "alias_fact", "query": "SOJ是什么？", "expected_keywords": ["stone of jordan", "乔丹"]},
    {"category": "alias_fact", "query": "超市是什么？", "expected_keywords": ["chaos sanctuary", "超市"]},
    {"category": "numeric", "query": "我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？", "expected_keywords": ["sorceress", "spirit", "breakpoint", "fcr"]},
    {"category": "numeric", "query": "地狱劳模火抗多少？", "expected_keywords": ["mephisto", "75", "fire"]},
    {"category": "strategy", "query": "我想玩锤丁，谜团底材去哪里刷最高效？", "expected_keywords": ["enigma", "mage plate", "cow", "pit", "ancient tunnels"]},
]

LLM_CASES = [
    {"category": "numeric_answer", "query": "我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？", "expected_markers": ["105", "117", "Spirit"]},
    {"category": "strategy_answer", "query": "我想玩锤丁，谜团底材去哪里刷最高效？", "expected_markers": ["Mage Plate", "Enigma", "The Secret Cow Level"]},
]


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def joined_chunk_text(chunks: list[dict[str, object]], top_k: int = 3) -> str:
    parts: list[str] = []
    for row in chunks[:top_k]:
        metadata = row.get("metadata", {}) or {}
        parts.append(str(metadata.get("title", "")))
        parts.append(str(row.get("text", ""))[:600])
    return normalize("\n".join(parts))


def evaluate_retrieval_case(service: Diablo2QAService, case: dict[str, object]) -> dict[str, object]:
    body = service.answer(str(case["query"]), use_llm=False)
    haystack = joined_chunk_text(body.get("chunks", []))
    expected_keywords = [normalize(str(item)) for item in case["expected_keywords"]]
    matched = [keyword for keyword in expected_keywords if keyword in haystack]
    top = (body.get("chunks") or [{}])[0]
    return {
        "category": case["category"],
        "query": case["query"],
        "retrieval_backend": body.get("retrieval_backend"),
        "query_type": body.get("query_context", {}).get("query_type"),
        "top_title": top.get("metadata", {}).get("title"),
        "top_source_id": top.get("metadata", {}).get("source_id"),
        "top_retrieval_source": top.get("retrieval_source"),
        "matched_keywords": matched,
        "expected_keywords": expected_keywords,
        "pass_top3_keyword": bool(matched),
        "ranking_reasons": body.get("ranking_reasons", [])[:3],
        "reason_summary": body.get("reason_summary"),
    }


def evaluate_llm_case(service: Diablo2QAService, case: dict[str, object]) -> dict[str, object]:
    body = service.answer(str(case["query"]), use_llm=True)
    answer = str(body.get("answer") or "")
    normalized_answer = normalize(answer)
    expected_markers = [str(item) for item in case["expected_markers"]]
    matched = [marker for marker in expected_markers if normalize(marker) in normalized_answer]
    return {
        "category": case["category"],
        "query": case["query"],
        "retrieval_backend": body.get("retrieval_backend"),
        "answer_release_ready": body.get("answer_release_ready"),
        "answer_verification": body.get("answer_verification"),
        "matched_markers": matched,
        "expected_markers": expected_markers,
        "pass_answer_markers": len(matched) == len(expected_markers),
        "answer_preview": answer[:800],
        "answer_sources": body.get("answer_sources", []),
    }


def summarize(rows: list[dict[str, object]], field: str) -> dict[str, int]:
    passed = sum(1 for row in rows if row.get(field))
    return {"passed": passed, "total": len(rows)}


def write_report(report: dict[str, object]) -> tuple[Path, Path]:
    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "current-pg-effect-eval.json"
    md_path = out_dir / "current-pg-effect-eval.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Current PostgreSQL QA Effect Evaluation",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Retrieval summary: `{report['retrieval_summary']['passed']}/{report['retrieval_summary']['total']}`",
        f"- LLM summary: `{report['llm_summary']['passed']}/{report['llm_summary']['total']}`",
        "- Rule: retrieval cases count as pass when expected keywords appear in top-3 chunk title/text; LLM cases count as pass when expected markers appear and release gate passes.",
        "",
        "## Retrieval Cases",
        "",
    ]
    for row in report["retrieval_cases"]:
        status = "PASS" if row["pass_top3_keyword"] else "GAP"
        lines.extend(
            [
                f"### [{status}] {row['query']}",
                f"- category: `{row['category']}`",
                f"- backend: `{row['retrieval_backend']}`",
                f"- query_type: `{row['query_type']}`",
                f"- top_title: `{row['top_title']}`",
                f"- top_source_id: `{row['top_source_id']}`",
                f"- top_retrieval_source: `{row['top_retrieval_source']}`",
                f"- matched_keywords: `{row['matched_keywords']}`",
                f"- reason_summary: `{row['reason_summary']}`",
                "",
            ]
        )
    lines.extend(["## LLM Cases", ""])
    for row in report["llm_cases"]:
        status = "PASS" if row["pass_answer_markers"] and row["answer_release_ready"] else "GAP"
        lines.extend(
            [
                f"### [{status}] {row['query']}",
                f"- category: `{row['category']}`",
                f"- backend: `{row['retrieval_backend']}`",
                f"- answer_release_ready: `{row['answer_release_ready']}`",
                f"- matched_markers: `{row['matched_markers']}`",
                f"- verifier_summary: `{row['answer_verification'].get('summary', '')}`",
                "",
            ]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    service = Diablo2QAService()
    retrieval_rows = [evaluate_retrieval_case(service, case) for case in RETRIEVAL_CASES]
    llm_rows = [evaluate_llm_case(service, case) for case in LLM_CASES]
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "retrieval_summary": summarize(retrieval_rows, "pass_top3_keyword"),
        "llm_summary": {
            "passed": sum(1 for row in llm_rows if row.get("pass_answer_markers") and row.get("answer_release_ready")),
            "total": len(llm_rows),
        },
        "retrieval_cases": retrieval_rows,
        "llm_cases": llm_rows,
    }
    json_path, md_path = write_report(report)
    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False))
    print(json.dumps(report["retrieval_summary"], ensure_ascii=False))
    print(json.dumps(report["llm_summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
