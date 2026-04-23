from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from .harness import make_service


class LLMCaseState(TypedDict, total=False):
    query: str
    markers: list[str]
    body: dict[str, Any]
    failures: list[str]


def _run_query(state: LLMCaseState) -> LLMCaseState:
    service = make_service()
    body = service.answer(state["query"], use_llm=True)
    return {**state, "body": body, "failures": list(state.get("failures", []))}


def _check_answer(state: LLMCaseState) -> LLMCaseState:
    body = state["body"]
    answer = str(body.get("answer") or "")
    failures = list(state.get("failures", []))

    if body.get("retrieval_backend") not in {"postgres-hybrid", "postgres-bm25", "postgres-lexical", "postgres-vector"}:
        failures.append("retrieval backend is not postgres-backed")
    if not body.get("reason_summary"):
        failures.append("reason_summary missing")
    if not body.get("answer_release_ready"):
        failures.append("answer release gate failed")
    if not body.get("answer_verification", {}).get("citation_gate_passed"):
        failures.append("citation gate failed")
    if not body.get("answer_verification", {}).get("grounding_gate_passed"):
        failures.append("grounding gate failed")
    if not body.get("answer_sources"):
        failures.append("answer_sources missing")

    for marker in state.get("markers", []):
        if marker.lower() not in answer.lower():
            failures.append(f"answer missing marker: {marker}")

    return {**state, "failures": failures}


def build_case_graph():
    graph = StateGraph(LLMCaseState)
    graph.add_node("run_query", _run_query)
    graph.add_node("check_answer", _check_answer)
    graph.add_edge(START, "run_query")
    graph.add_edge("run_query", "check_answer")
    graph.add_edge("check_answer", END)
    return graph.compile()
