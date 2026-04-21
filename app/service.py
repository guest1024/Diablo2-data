from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .chroma_store import ChromaStore
from .config import ROOT
from .graph_store import GraphStore
from .llm_client import answer_question
from .query_normalizer import QueryNormalizer


class Diablo2QAService:
    def __init__(self) -> None:
        self.graph = GraphStore()
        self.chroma = ChromaStore()
        self.normalizer = QueryNormalizer()

    def ingest(self) -> dict[str, int]:
        return self.chroma.ingest(
            ROOT / "docs/chroma-ready/documents.jsonl",
            ROOT / "docs/chroma-ready/chunks.jsonl",
        )

    def answer(self, query: str, use_llm: bool = True) -> dict[str, Any]:
        query_context = self.normalizer.expand(query)
        retrieval_query = str(query_context["expanded_query"])
        entities = self.graph.resolve_entities(
            retrieval_query,
            preferred_terms=list(query_context.get("preferred_terms", [])),
            canonical_hints=list(query_context.get("canonical_hints", [])),
        )
        canonical_ids = [row["canonical_id"] for row in entities]
        grounding = self.graph.get_grounding(canonical_ids)
        confident_entity_ids = self._select_confident_entity_ids(entities, query_context)
        chunks = self.chroma.query_chunks(
            retrieval_query,
            top_k=6,
            entity_ids=confident_entity_ids,
            preferred_terms=list(query_context.get("preferred_terms", [])),
            preferred_title_contains=list(query_context.get("preferred_title_contains", [])),
            preferred_text_contains=list(query_context.get("preferred_text_contains", [])),
            preferred_source_ids=list(query_context.get("preferred_source_ids", [])),
            discouraged_source_ids=list(query_context.get("discouraged_source_ids", [])),
        )
        payload = {
            "query": query,
            "query_context": query_context,
            "confident_entity_ids": confident_entity_ids,
            "resolved_entities": entities,
            "claims": grounding["claims"],
            "provenance": grounding["provenance"],
            "chunks": chunks,
        }
        if not use_llm:
            return payload

        prompt = (
            "问题：\n"
            f"{query}\n\n"
            "查询扩展：\n"
            f"{json.dumps(query_context, ensure_ascii=False, indent=2)}\n\n"
            "已解析实体：\n"
            f"{json.dumps(entities, ensure_ascii=False, indent=2)}\n\n"
            "结构化事实：\n"
            f"{json.dumps(grounding['claims'], ensure_ascii=False, indent=2)}\n\n"
            "来源信息：\n"
            f"{json.dumps(grounding['provenance'], ensure_ascii=False, indent=2)}\n\n"
            "证据文本：\n"
            f"{json.dumps(chunks, ensure_ascii=False, indent=2)}\n\n"
            "请给出一个简明准确的回答，并列出关键来源 URL。"
        )
        payload["answer"] = answer_question(prompt)
        return payload

    @staticmethod
    def _select_confident_entity_ids(entities: list[dict[str, Any]], query_context: dict[str, Any]) -> list[str]:
        if not entities:
            return []
        if "curated-anchor" in set(query_context.get("preferred_source_ids", [])):
            return []
        has_canonical_hint = bool(query_context.get("canonical_hints"))
        if has_canonical_hint:
            return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 1.0][:3]

        top_score = float(entities[0].get("score", 0.0))
        second_score = float(entities[1].get("score", 0.0)) if len(entities) > 1 else 0.0
        if top_score >= 0.75 and top_score - second_score >= 0.15:
            return [entities[0]["canonical_id"]]
        return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 1.0][:3]
