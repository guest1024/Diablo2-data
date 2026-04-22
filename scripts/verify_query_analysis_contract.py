#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    chroma_dir = ROOT / ".data/chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
    chroma_dir.mkdir(parents=True, exist_ok=True)

    service = Diablo2QAService()
    service.ingest()

    cases = {
        "精神盾底材是什么": {
            "intent": "crafting_base",
            "min_retrieval_queries": 3,
            "expects_subquestions": True,
            "must_contain_retrieval_queries": ["Spirit Shield", "Monarch"],
        },
        "军帽哪里刷": {
            "intent": "farming",
            "min_retrieval_queries": 3,
            "expects_subquestions": True,
            "must_contain_retrieval_queries": ["Harlequin Crest"],
        },
        "地穴适合干什么": {
            "intent": "usage",
            "min_retrieval_queries": 3,
            "expects_subquestions": True,
            "must_contain_retrieval_queries": ["The Pit"],
        },
        "超市怎么走": {
            "intent": "location",
            "min_retrieval_queries": 3,
            "expects_subquestions": True,
            "must_contain_retrieval_queries": ["Chaos Sanctuary"],
        },
        "乔丹戒指是什么": {
            "intent": "definition",
            "min_retrieval_queries": 2,
            "expects_subquestions": False,
            "expected_entity_query": "The Stone of Jordan Unique Ring",
            "expected_matched_terms": ["乔丹"],
        },
        "乔丹是什么": {
            "intent": "definition",
            "min_retrieval_queries": 3,
            "expects_subquestions": False,
            "expected_entity_query": "Stone of Jordan",
            "expected_matched_terms": ["乔丹"],
        },
        "新星电法是什么": {
            "intent": "definition",
            "min_retrieval_queries": 3,
            "expects_subquestions": False,
            "expected_entity_query": "Nova Sorceress",
            "expected_matched_terms": ["新星电法"],
        },
        "无限符文之语底材": {
            "intent": "crafting_base",
            "min_retrieval_queries": 3,
            "expects_subquestions": True,
            "must_contain_retrieval_queries": ["Infinity", "base requirement", "底材"],
        },
        "新星电法配装怎么玩，想走 ES 体系的话会用 Memory 预buff，自持 Infinity Scythe 的练法一般怎么搭？": {
            "intent": "build",
            "min_retrieval_queries": 4,
            "expects_subquestions": True,
            "expected_entity_query": "Nova Sorceress",
            "expected_matched_terms": ["新星电法"],
            "must_contain_retrieval_queries": ["Nova Sorceress", "Memory", "Infinity Scythe"],
            "must_contain_subquestions": ["Memory", "Infinity Scythe"],
        },
    }

    for query, expected in cases.items():
        analysis = service.analyze_query(query, use_llm=False)
        expect(analysis["intent"] == expected["intent"], f"{query} intent classified as {expected['intent']}")
        expect(bool(analysis["rewritten_queries"]), f"{query} has rewritten queries")
        expect(len(analysis["retrieval_queries"]) >= expected["min_retrieval_queries"], f"{query} has enough retrieval queries")
        expect(bool(analysis["entity_query"]), f"{query} has entity query")
        if "expected_entity_query" in expected:
            expect(analysis["entity_query"] == expected["expected_entity_query"], f"{query} keeps stable entity query")
        if "expected_matched_terms" in expected:
            expect(analysis["matched_terms"] == expected["expected_matched_terms"], f"{query} keeps precise matched terms")
        if "must_contain_retrieval_queries" in expected:
            retrieval_blob = "\n".join(analysis["retrieval_queries"])
            for snippet in expected["must_contain_retrieval_queries"]:
                expect(snippet in retrieval_blob, f"{query} retrieval plan keeps facet: {snippet}")
        if "must_contain_subquestions" in expected:
            sub_blob = "\n".join(analysis["subquestions"])
            for snippet in expected["must_contain_subquestions"]:
                expect(snippet in sub_blob, f"{query} subquestions keep facet: {snippet}")
        expect(analysis["used_llm"] is False, f"{query} deterministic analysis avoids external LLM in contract test")
        if expected["expects_subquestions"]:
            expect(bool(analysis["subquestions"]), f"{query} emits stable subquestions")
        else:
            expect(not analysis["subquestions"], f"{query} keeps simple queries undecomposed")

    body = service.answer("精神盾底材是什么", use_llm=False)
    expect(body["query_analysis"]["intent"] == "crafting_base", "QA payload exposes query analysis")
    expect(bool(body["retrieval_plan"]), "QA payload exposes retrieval plan")
    expect(any(row.get("route_contributions") for row in body["evidence_chunks"]), "QA evidence chunks keep route contributions")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
