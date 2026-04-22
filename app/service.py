from __future__ import annotations

import json
from typing import Any

from .chroma_store import ChromaStore
from .config import ROOT
from .graph_store import GraphStore
from .llm_client import answer_question
from .query_analyzer import QueryAnalyzer


class Diablo2QAService:
    def __init__(self) -> None:
        self.graph = GraphStore()
        self.chroma = ChromaStore()
        self.analyzer = QueryAnalyzer()

    def ingest(self) -> dict[str, int]:
        return self.chroma.ingest(
            ROOT / "docs/chroma-ready/documents.jsonl",
            ROOT / "docs/chroma-ready/chunks.jsonl",
        )

    def analyze_query(self, query: str, *, use_llm: bool = False) -> dict[str, Any]:
        return self.analyzer.analyze(query, use_llm=use_llm)

    def answer(self, query: str, use_llm: bool = True) -> dict[str, Any]:
        query_analysis = self.analyze_query(query, use_llm=use_llm)
        entity_query = str(query_analysis.get("entity_query", query_analysis["normalized_query"]))
        entities = self.graph.resolve_entities(
            entity_query,
            preferred_terms=list(query_analysis.get("preferred_terms", [])),
            canonical_hints=list(query_analysis.get("canonical_hints", [])),
        )
        confident_entity_ids = self._select_confident_entity_ids(entities, query_analysis)
        grounding = self.graph.get_grounding(confident_entity_ids)
        chunks = self.chroma.query_chunks_multi(
            list(query_analysis.get("retrieval_plan", [])),
            top_k=8,
            entity_ids=confident_entity_ids,
            preferred_terms=list(query_analysis.get("preferred_terms", [])),
            preferred_title_contains=list(query_analysis.get("preferred_title_contains", [])),
            preferred_text_contains=list(query_analysis.get("preferred_text_contains", [])),
            preferred_source_ids=list(query_analysis.get("preferred_source_ids", [])),
            discouraged_source_ids=list(query_analysis.get("discouraged_source_ids", [])),
        )
        evidence_chunks = self._build_evidence_chunks(chunks)
        sources = self._collect_sources(grounding["provenance"], evidence_chunks)

        payload = {
            "query": query,
            "language": query_analysis["language"],
            "query_analysis": query_analysis,
            "retrieval_plan": query_analysis.get("retrieval_plan", []),
            "confident_entity_ids": confident_entity_ids,
            "grounding_entity_ids": confident_entity_ids,
            "grounding_mode": self._grounding_mode(confident_entity_ids, evidence_chunks),
            "resolved_entities": entities,
            "claims": grounding["claims"],
            "provenance": grounding["provenance"],
            "sources": sources,
            "evidence_chunks": evidence_chunks,
            "chunks": chunks,
        }
        if not use_llm:
            return payload

        prompt = self._build_answer_prompt(query, payload)
        try:
            payload["answer"] = answer_question(prompt)
        except Exception as exc:
            payload["llm_error"] = str(exc)
            payload["answer"] = self._build_grounded_fallback_answer(query, payload)
        return payload

    def _build_answer_prompt(self, query: str, payload: dict[str, Any]) -> str:
        return (
            "问题：\n"
            f"{query}\n\n"
            "查询分析：\n"
            f"{json.dumps(payload['query_analysis'], ensure_ascii=False, indent=2)}\n\n"
            "已解析实体：\n"
            f"{json.dumps(payload['resolved_entities'], ensure_ascii=False, indent=2)}\n\n"
            "结构化事实：\n"
            f"{json.dumps(payload['claims'], ensure_ascii=False, indent=2)}\n\n"
            "来源信息：\n"
            f"{json.dumps(payload['sources'], ensure_ascii=False, indent=2)}\n\n"
            "证据文本：\n"
            f"{json.dumps(payload['evidence_chunks'], ensure_ascii=False, indent=2)}\n\n"
            "请基于结构化事实与证据文本回答。若结构化事实不足，则优先依据证据文本。"
            "输出必须包含：1）结论；2）关键事实；3）来源 URL；4）如果证据不足，明确指出。"
        )

    def _build_grounded_fallback_answer(self, query: str, payload: dict[str, Any]) -> str:
        facts: list[str] = []
        for claim in payload.get("claims", [])[:3]:
            subject = str(claim.get("subject_id", "")).strip()
            predicate = str(claim.get("predicate", "")).strip()
            obj = str(claim.get("object", "")).strip()
            snippet = " ".join(part for part in [subject, predicate, obj] if part)
            if snippet:
                facts.append(f"- {snippet}")
        if not facts:
            for chunk in payload.get("evidence_chunks", [])[:2]:
                title = str(chunk.get("title", "")).strip()
                text = " ".join(str(chunk.get("text", "")).split())
                preview = text[:220]
                if title or preview:
                    facts.append(f"- {title}: {preview}")

        source_lines = [f"- {row['url']}" for row in payload.get("sources", [])[:3] if row.get("url")]
        if not source_lines:
            source_lines = ["- 无可用来源 URL"]

        return (
            "结论：当前外部 LLM 不可用，以下为基于已检索证据生成的降级回答。\n"
            f"问题：{query}\n\n"
            "关键事实：\n"
            f"{chr(10).join(facts) if facts else '- 暂无足够结构化事实'}\n\n"
            "来源 URL：\n"
            f"{chr(10).join(source_lines)}"
        )

    @staticmethod
    def _select_confident_entity_ids(entities: list[dict[str, Any]], query_analysis: dict[str, Any]) -> list[str]:
        if not entities:
            return []
        if "curated-anchor" in set(query_analysis.get("preferred_source_ids", [])):
            return []

        has_canonical_hint = bool(query_analysis.get("canonical_hints"))
        top_score = float(entities[0].get("score", 0.0))
        second_score = float(entities[1].get("score", 0.0)) if len(entities) > 1 else 0.0

        if has_canonical_hint and top_score >= 1.2 and top_score - second_score >= 0.15:
            return [entities[0]["canonical_id"]]
        if has_canonical_hint:
            return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 1.0][:3]
        if top_score >= 0.75 and top_score - second_score >= 0.15:
            return [entities[0]["canonical_id"]]
        return [row["canonical_id"] for row in entities if float(row.get("score", 0.0)) >= 1.0][:3]

    @staticmethod
    def _build_evidence_chunks(chunks: list[dict[str, Any]], limit: int = 4) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for row in chunks[:limit]:
            metadata = dict(row.get("metadata", {}))
            evidence.append(
                {
                    "chunk_id": row.get("chunk_id"),
                    "title": metadata.get("title"),
                    "source_id": metadata.get("source_id"),
                    "source_url": metadata.get("source"),
                    "authority_tier": metadata.get("authority_tier"),
                    "retrieval_source": row.get("retrieval_source"),
                    "aggregate_score": row.get("aggregate_score", row.get("score")),
                    "route_contributions": row.get("route_contributions", []),
                    "text": row.get("text"),
                }
            )
        return evidence

    @staticmethod
    def _collect_sources(provenance: list[dict[str, Any]], evidence_chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str]] = set()
        sources: list[dict[str, Any]] = []
        for row in provenance:
            url = Diablo2QAService._normalize_url(row.get("evidence_url"))
            source_id = str(row.get("source_id", "")).strip()
            key = (source_id, url)
            if not url or key in seen:
                continue
            seen.add(key)
            sources.append(
                {
                    "source_id": source_id,
                    "url": url,
                    "authority_tier": row.get("authority_tier"),
                    "via": "provenance",
                }
            )
        for row in evidence_chunks:
            url = Diablo2QAService._normalize_url(row.get("source_url"))
            source_id = str(row.get("source_id", "")).strip()
            key = (source_id, url)
            if not url or key in seen:
                continue
            seen.add(key)
            sources.append(
                {
                    "source_id": source_id,
                    "url": url,
                    "authority_tier": row.get("authority_tier"),
                    "title": row.get("title"),
                    "via": row.get("retrieval_source"),
                }
            )
        return sources

    @staticmethod
    def _normalize_url(value: Any) -> str:
        text = str(value or "").strip()
        if text.lower() in {"", "none", "null"}:
            return ""
        return text

    @staticmethod
    def _grounding_mode(confident_entity_ids: list[str], evidence_chunks: list[dict[str, Any]]) -> str:
        if confident_entity_ids:
            return "graph+evidence"
        if any(row.get("source_id") == "curated-anchor" for row in evidence_chunks):
            return "curated-evidence"
        return "retrieval-only"
