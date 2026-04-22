#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the Diablo II first-system API.")
    parser.add_argument("--with-llm", action="store_true", help="Also test the LLM-backed QA path.")
    args = parser.parse_args()

    client = TestClient(app)

    health = client.get("/health")
    health.raise_for_status()
    print("HEALTH", json.dumps(health.json(), ensure_ascii=False))

    ingest = client.post("/ingest")
    ingest.raise_for_status()
    print("INGEST", json.dumps(ingest.json(), ensure_ascii=False))

    analysis = client.post("/analyze-query", json={"query": "精神盾底材是什么", "use_llm": False})
    analysis.raise_for_status()
    analysis_body = analysis.json()
    print(
        "ANALYZE",
        json.dumps(
            {
                "query": analysis_body.get("original_query"),
                "intent": analysis_body.get("intent"),
                "complexity": analysis_body.get("complexity"),
                "retrieval_queries": analysis_body.get("retrieval_queries"),
                "subquestions": analysis_body.get("subquestions"),
            },
            ensure_ascii=False,
        ),
    )

    queries = [
        "Spirit 是什么？",
        "军帽是什么？",
        "精神符文之语是什么？",
        "What is Hellfire Torch?",
    ]

    for query in queries:
        response = client.post("/qa", json={"query": query, "use_llm": False})
        response.raise_for_status()
        body = response.json()
        print(
            "QA",
            json.dumps(
                {
                    "query": query,
                    "resolved_entities": len(body.get("resolved_entities", [])),
                    "top_chunk_title": (body.get("chunks") or [{}])[0].get("metadata", {}).get("title"),
                    "top_chunk_source": (body.get("chunks") or [{}])[0].get("retrieval_source"),
                },
                ensure_ascii=False,
            ),
        )

    if args.with_llm:
        response = client.post("/qa", json={"query": "What is Hellfire Torch?", "use_llm": True})
        response.raise_for_status()
        body = response.json()
        print(
            "LLM_QA",
            json.dumps(
                {
                    "answer_preview": (body.get("answer") or "")[:300],
                },
                ensure_ascii=False,
            ),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
