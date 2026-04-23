from __future__ import annotations

import json
from typing import Any

from .chroma_store import ChromaStore
from .config import ROOT
from .graph_store import GraphStore
from .llm_client import answer_question
from .query_understanding import QueryUnderstandingEngine


class Diablo2QAService:
    def __init__(self) -> None:
        self.graph = GraphStore()
        self.chroma = ChromaStore()
        self.query_understanding = QueryUnderstandingEngine()

    def ingest(self) -> dict[str, int]:
        return self.chroma.ingest(
            ROOT / "docs/chroma-ready/documents.jsonl",
            ROOT / "docs/chroma-ready/chunks.jsonl",
        )

    def answer(self, query: str, use_llm: bool = True) -> dict[str, Any]:
        query_context = self.query_understanding.analyze(query)
        retrieval_query = str(query_context["expanded_query"])

        entity_candidates = self._resolve_entities_for_rewrites(query_context)
        canonical_ids = [row["canonical_id"] for row in entity_candidates]
        grounding = self.graph.get_grounding(canonical_ids)
        confident_entity_ids = self._select_confident_entity_ids(entity_candidates, query_context)
        chunks = self._retrieve_chunks(query_context, entity_candidates, confident_entity_ids)

        payload = {
            "query": query,
            "query_context": query_context,
            "retrieval_query": retrieval_query,
            "resolved_entities": entity_candidates,
            "confident_entity_ids": confident_entity_ids,
            "claims": grounding["claims"],
            "provenance": grounding["provenance"],
            "chunks": chunks,
            "retrieval_trace": {
                "query_type": query_context.get("query_type"),
                "intent_label": query_context.get("intent_label"),
                "matched_patterns": query_context.get("matched_patterns", []),
                "matched_aliases": query_context.get("matched_aliases", []),
                "accepted_rewrite": query_context.get("accepted_rewrite"),
                "rewrite_candidates": query_context.get("rewrite_candidates", []),
                "subquestion_plan": query_context.get("subquestion_plan"),
                "retrieval_policy": query_context.get("retrieval_policy"),
                "retrieval_plan": query_context.get("retrieval_plan", []),
                "answer_constraints": query_context.get("answer_constraints"),
            },
            "structured_support": query_context.get("structured_support", {}),
        }
        if not use_llm:
            return payload

        prompt = (
            "问题：\n"
            f"{query}\n\n"
            "Query Understanding：\n"
            f"{json.dumps(payload['retrieval_trace'], ensure_ascii=False, indent=2)}\n\n"
            "结构化支撑：\n"
            f"{json.dumps(payload['structured_support'], ensure_ascii=False, indent=2)}\n\n"
            "实体解析：\n"
            f"{json.dumps(entity_candidates, ensure_ascii=False, indent=2)}\n\n"
            "结构化事实：\n"
            f"{json.dumps(grounding['claims'], ensure_ascii=False, indent=2)}\n\n"
            "来源信息：\n"
            f"{json.dumps(grounding['provenance'], ensure_ascii=False, indent=2)}\n\n"
            "证据文本：\n"
            f"{json.dumps(chunks, ensure_ascii=False, indent=2)}\n\n"
            "请基于给定证据回答，优先使用结构化支撑与证据文本。"
            "不要补造未被证据支持的事实；数值问题不要线性插值；最后列出关键来源 URL。"
        )
        payload["answer"] = answer_question(prompt)
        return payload

    def _resolve_entities_for_rewrites(self, query_context: dict[str, Any]) -> list[dict[str, Any]]:
        aggregated: dict[str, dict[str, Any]] = {}
        rewrite_candidates = [row for row in query_context.get("rewrite_candidates", []) if row.get("accepted")]
        if not rewrite_candidates:
            rewrite_candidates = [query_context.get("accepted_rewrite") or {"rewrite_text": query_context.get("expanded_query", query_context.get("normalized_query", ""))}]

        for rewrite in rewrite_candidates[:3]:
            rewrite_text = str(rewrite.get("rewrite_text") or "").strip()
            if not rewrite_text:
                continue
            entities = self.graph.resolve_entities(
                rewrite_text,
                preferred_terms=list(query_context.get("preferred_terms", [])),
                canonical_hints=list(query_context.get("canonical_hints", [])),
            )
            for entity in entities:
                canonical_id = entity["canonical_id"]
                enriched = dict(entity)
                enriched["matched_rewrite"] = rewrite_text
                enriched["matched_rewrite_kind"] = rewrite.get("rewrite_kind")
                enriched["rewrite_confidence"] = rewrite.get("confidence")
                if canonical_id not in aggregated or float(enriched.get("score", 0.0)) > float(aggregated[canonical_id].get("score", 0.0)):
                    aggregated[canonical_id] = enriched
        ordered = list(aggregated.values())
        ordered.sort(key=lambda row: (-float(row.get("score", 0.0)), str(row.get("entity", {}).get("name", ""))))
        return ordered[:10]

    def _retrieve_chunks(
        self,
        query_context: dict[str, Any],
        entities: list[dict[str, Any]],
        confident_entity_ids: list[str],
    ) -> list[dict[str, Any]]:
        combined: dict[str, dict[str, Any]] = {}
        rewrite_candidates = [row for row in query_context.get("rewrite_candidates", []) if row.get("accepted")]
        if not rewrite_candidates:
            rewrite_candidates = [query_context.get("accepted_rewrite") or {"rewrite_text": query_context.get("expanded_query", "")}]

        top_k = 8
        for lane in query_context.get("retrieval_plan", []):
            top_k = max(top_k, int(lane.get("target_k") or 0))

        for rewrite_index, rewrite in enumerate(rewrite_candidates[:3], start=1):
            rewrite_text = str(rewrite.get("rewrite_text") or "").strip()
            if not rewrite_text:
                continue
            chunk_rows = self.chroma.query_chunks(
                rewrite_text,
                top_k=top_k,
                entity_ids=confident_entity_ids,
                preferred_terms=list(query_context.get("preferred_terms", [])),
                preferred_title_contains=list(query_context.get("preferred_title_contains", [])),
                preferred_text_contains=list(query_context.get("preferred_text_contains", [])),
                preferred_source_ids=list(query_context.get("preferred_source_ids", [])),
                discouraged_source_ids=list(query_context.get("discouraged_source_ids", [])),
            )
            for row in chunk_rows:
                chunk_id = row["chunk_id"]
                retrieval_source = str(row.get("retrieval_source") or "")
                source_bonus = {"entity_link": 4.0, "lexical": 3.0, "vector": 2.0}.get(retrieval_source, 1.0)
                rewrite_bonus = max(0.0, 3.0 - (rewrite_index - 1) * 0.75)
                lexical_bonus = float(row.get("score", 0.0)) * 0.1
                vector_bonus = 0.0
                if row.get("distance") is not None:
                    vector_bonus = max(0.0, 1.5 - float(row.get("distance", 0.0)))
                final_score = round(source_bonus + rewrite_bonus + lexical_bonus + vector_bonus, 4)
                enriched = dict(row)
                enriched["matched_rewrite"] = rewrite_text
                enriched["matched_rewrite_kind"] = rewrite.get("rewrite_kind")
                enriched["query_type"] = query_context.get("query_type")
                enriched["final_score"] = final_score
                existing = combined.get(chunk_id)
                if existing is None or final_score > float(existing.get("final_score", 0.0)):
                    combined[chunk_id] = enriched

        ordered = list(combined.values())
        ordered.sort(
            key=lambda row: (
                -float(row.get("final_score", 0.0)),
                row.get("distance") is None,
                float(row.get("distance", 999999.0)) if row.get("distance") is not None else 999999.0,
                -float(row.get("score", 0.0)),
            )
        )
        return ordered[:8]

    @staticmethod
    def _select_confident_entity_ids(entities: list[dict[str, Any]], query_context: dict[str, Any]) -> list[str]:
        if not entities:
            return []
        if "curated-anchor" in set(query_context.get("preferred_source_ids", [])):
            return []
        has_canonical_hint = bool(query_context.get("canonical_hints"))
        if has_canonical_hint:
            return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 1.0][:4]

        top_score = float(entities[0].get("score", 0.0))
        second_score = float(entities[1].get("score", 0.0)) if len(entities) > 1 else 0.0
        if top_score >= 0.75 and top_score - second_score >= 0.15:
            return [entities[0]["canonical_id"]]
        return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 0.85][:4]
