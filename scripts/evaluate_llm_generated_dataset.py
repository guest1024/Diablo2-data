#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService

DEFAULT_DATASET_PATH = ROOT / "docs/tier0/evals/llm-generated-query-eval-dataset.json"
OUT_DIR = ROOT / "docs/tier0/evals"


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


def contains_ci(haystack: str, needle: str) -> bool:
    return normalize(needle) in normalize(haystack)


def evaluate_case(service: Diablo2QAService, case: dict[str, object], *, use_llm: bool) -> dict[str, object]:
    query = str(case["query"])
    body = service.answer(query, use_llm=use_llm)
    query_analysis = dict(body.get("query_analysis", {}))
    top_chunk = (body.get("chunks") or [{}])[0]
    metadata = dict(top_chunk.get("metadata", {}))

    checks: dict[str, bool] = {}
    expected_intent = case.get("expected_intent")
    expected_needs_decomposition = case.get("expected_needs_decomposition")
    expected_entity_query_contains = case.get("expected_entity_query_contains")
    expected_source_id = case.get("expected_source_id")
    expected_title_contains = case.get("expected_title_contains")
    expected_grounding_mode = case.get("expected_grounding_mode")

    if expected_intent is not None:
        checks["intent"] = query_analysis.get("intent") == expected_intent
    if expected_needs_decomposition is not None:
        checks["needs_decomposition"] = bool(query_analysis.get("needs_decomposition")) == bool(expected_needs_decomposition)
    if expected_entity_query_contains:
        checks["entity_query"] = contains_ci(str(query_analysis.get("entity_query", "")), str(expected_entity_query_contains))
    if expected_source_id:
        checks["top_source_id"] = str(metadata.get("source_id", "")) == str(expected_source_id)
    if expected_title_contains:
        checks["top_title"] = contains_ci(str(metadata.get("title", "")), str(expected_title_contains))
    if expected_grounding_mode:
        checks["grounding_mode"] = body.get("grounding_mode") == expected_grounding_mode

    passed_checks = sum(1 for value in checks.values() if value)
    total_checks = len(checks)
    return {
        "id": case.get("id"),
        "seed_id": case.get("seed_id"),
        "query": query,
        "case_type": case.get("case_type"),
        "use_llm": use_llm,
        "checks": checks,
        "passed": passed_checks == total_checks,
        "score": round(passed_checks / total_checks, 4) if total_checks else 1.0,
        "actual": {
            "intent": query_analysis.get("intent"),
            "needs_decomposition": query_analysis.get("needs_decomposition"),
            "entity_query": query_analysis.get("entity_query"),
            "top_source_id": metadata.get("source_id"),
            "top_title": metadata.get("title"),
            "grounding_mode": body.get("grounding_mode"),
            "top_retrieval_source": top_chunk.get("retrieval_source"),
        },
        "expected": {
            "intent": expected_intent,
            "needs_decomposition": expected_needs_decomposition,
            "entity_query_contains": expected_entity_query_contains,
            "top_source_id": expected_source_id,
            "top_title_contains": expected_title_contains,
            "grounding_mode": expected_grounding_mode,
        },
    }


def summarize(rows: list[dict[str, object]]) -> dict[str, object]:
    metric_pass: dict[str, int] = {}
    metric_total: dict[str, int] = {}
    by_type: dict[str, dict[str, int]] = {}
    by_expected_intent: dict[str, dict[str, int]] = {}
    by_grounding_mode: dict[str, dict[str, int]] = {}

    for row in rows:
        for metric, passed in dict(row.get("checks", {})).items():
            metric_total[metric] = metric_total.get(metric, 0) + 1
            metric_pass[metric] = metric_pass.get(metric, 0) + (1 if passed else 0)

        case_type = str(row.get("case_type", "unknown"))
        by_type.setdefault(case_type, {"passed": 0, "total": 0})
        by_type[case_type]["total"] += 1

        expected_intent = str(dict(row.get("expected", {})).get("intent") or "unknown")
        by_expected_intent.setdefault(expected_intent, {"passed": 0, "total": 0})
        by_expected_intent[expected_intent]["total"] += 1

        actual_grounding_mode = str(dict(row.get("actual", {})).get("grounding_mode") or "unknown")
        by_grounding_mode.setdefault(actual_grounding_mode, {"passed": 0, "total": 0})
        by_grounding_mode[actual_grounding_mode]["total"] += 1

        if row.get("passed"):
            by_type[case_type]["passed"] += 1
            by_expected_intent[expected_intent]["passed"] += 1
            by_grounding_mode[actual_grounding_mode]["passed"] += 1

    return {
        "passed": sum(1 for row in rows if row.get("passed")),
        "total": len(rows),
        "by_type": by_type,
        "by_expected_intent": by_expected_intent,
        "by_grounding_mode": by_grounding_mode,
        "metrics": {
            key: {"passed": metric_pass.get(key, 0), "total": metric_total.get(key, 0)}
            for key in sorted(metric_total)
        },
    }


def write_report(dataset_path: Path, rows: list[dict[str, object]], *, use_llm: bool) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = "llm-assisted" if use_llm else "retrieval-only"
    out_json = OUT_DIR / f"llm-generated-query-eval-report-{stem}.json"
    out_md = OUT_DIR / f"llm-generated-query-eval-report-{stem}.md"
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "use_llm": use_llm,
        "summary": summarize(rows),
        "rows": rows,
    }
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# LLM Generated Query Eval Report",
        "",
        f"- generated_at: `{report['generated_at']}`",
        f"- dataset_path: `{report['dataset_path']}`",
        f"- use_llm: `{use_llm}`",
        f"- passed: `{report['summary']['passed']}/{report['summary']['total']}`",
        "",
        "## By type",
        "",
    ]
    for case_type, row in report["summary"]["by_type"].items():
        lines.append(f"- {case_type}: `{row['passed']}/{row['total']}`")
    lines.extend(["", "## By expected intent", ""])
    for intent, row in report["summary"]["by_expected_intent"].items():
        lines.append(f"- {intent}: `{row['passed']}/{row['total']}`")
    lines.extend(["", "## By actual grounding mode", ""])
    for mode, row in report["summary"]["by_grounding_mode"].items():
        lines.append(f"- {mode}: `{row['passed']}/{row['total']}`")
    lines.extend(["", "## Metrics", ""])
    for metric, row in report["summary"]["metrics"].items():
        lines.append(f"- {metric}: `{row['passed']}/{row['total']}`")
    lines.extend(["", "## Failures", ""])
    failures = [row for row in rows if not row["passed"]]
    if not failures:
        lines.append("- none")
    else:
        for row in failures:
            lines.extend(
                [
                    f"### {row['query']}",
                    f"- case_type: `{row['case_type']}`",
                    f"- checks: `{json.dumps(row['checks'], ensure_ascii=False)}`",
                    f"- actual: `{json.dumps(row['actual'], ensure_ascii=False)}`",
                    f"- expected: `{json.dumps(row['expected'], ensure_ascii=False)}`",
                    "",
                ]
            )

    lines.extend(["", "## Cases by expected intent", ""])
    intent_groups: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        expected = dict(row.get("expected", {}))
        intent = str(expected.get("intent") or "unknown")
        intent_groups.setdefault(intent, []).append(row)
    for intent, intent_rows in intent_groups.items():
        lines.append(f"### {intent}")
        for row in intent_rows:
            actual = dict(row.get("actual", {}))
            status = "PASS" if row.get("passed") else "FAIL"
            lines.append(
                f"- [{status}] `{row['seed_id']}` | query=`{row['query']}` | actual_intent=`{actual.get('intent')}` | entity_query=`{actual.get('entity_query')}`"
            )
        lines.append("")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET_PATH))
    parser.add_argument("--use-llm", action="store_true")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    cases = list(dataset.get("cases", []))

    service = Diablo2QAService()
    service.ingest()
    rows = [evaluate_case(service, case, use_llm=args.use_llm) for case in cases]
    out_json = write_report(dataset_path, rows, use_llm=args.use_llm)
    print(json.dumps({"summary": summarize(rows), "report": str(out_json.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
