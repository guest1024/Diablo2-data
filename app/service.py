from __future__ import annotations

import json
import re
from typing import Any

from .chroma_store import ChromaStore
from .config import ROOT, settings
from .graph_store import GraphStore
from .llm_client import complete_json, complete_text, llm_available
from .postgres_store import PostgresRetrievalStore
from .query_understanding import QueryUnderstandingEngine


class Diablo2QAService:
    def __init__(self, chroma_persist_dir: Path | None = None) -> None:
        self.graph = GraphStore()
        self.chroma = ChromaStore(persist_dir=chroma_persist_dir)
        self.postgres = PostgresRetrievalStore()
        self.query_understanding = QueryUnderstandingEngine()

    def ingest(self) -> dict[str, int]:
        result = self.chroma.ingest(
            ROOT / "docs/chroma-ready/documents.jsonl",
            ROOT / "docs/chroma-ready/chunks.jsonl",
        )
        result["retrieval_backend"] = self._selected_backend_name()
        return result

    def runtime_status(self) -> dict[str, Any]:
        return {
            "retrieval_backend": self._selected_backend_name(),
            "postgres": self.postgres.health(),
            "graph_stats": self.graph.stats(),
        }

    def answer(self, query: str, use_llm: bool = True) -> dict[str, Any]:
        query_context = self.query_understanding.analyze(query)
        query_context["structured_support"] = self._dedupe_structured_support(query_context.get("structured_support", {}))
        retrieval_query = str(query_context["expanded_query"])

        entity_candidates = self._resolve_entities_for_rewrites(query_context)
        canonical_ids = [row["canonical_id"] for row in entity_candidates]
        grounding = self.postgres.get_grounding(canonical_ids) if self._selected_backend_name() == "postgres" else {"claims": [], "provenance": []}
        if not grounding.get("claims") and not grounding.get("provenance"):
            grounding = self.graph.get_grounding(canonical_ids)
        confident_entity_ids = self._select_confident_entity_ids(entity_candidates, query_context)
        chunks, actual_backend = self._retrieve_chunks(query_context, confident_entity_ids)
        chunks = self._merge_structured_evidence(query_context, chunks)
        ranking_reasons = self._build_ranking_reasons(query_context, chunks)
        ranking_reasons = self._dedupe_ranking_reasons(ranking_reasons)
        reason_summary = self._build_reason_summary(query_context, ranking_reasons)
        numeric_reasoning_summary = self._build_numeric_reasoning_summary(query_context)
        source_catalog = self._build_source_catalog(chunks, grounding["provenance"])

        payload = {
            "query": query,
            "query_context": query_context,
            "retrieval_query": retrieval_query,
            "retrieval_backend": actual_backend,
            "configured_retrieval_backend": self._selected_backend_name(),
            "resolved_entities": entity_candidates,
            "confident_entity_ids": confident_entity_ids,
            "claims": grounding["claims"],
            "provenance": grounding["provenance"],
            "chunks": chunks,
            "ranking_reasons": ranking_reasons,
            "reason_summary": reason_summary,
            "numeric_reasoning_summary": numeric_reasoning_summary,
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
                "configured_backend": self._selected_backend_name(),
                "actual_backend": actual_backend,
            },
            "structured_support": query_context.get("structured_support", {}),
            "answer_source_catalog": source_catalog,
        }
        if not use_llm:
            return payload

        generation = self._answer_with_release_gate(
            query=query,
            payload=payload,
            entity_candidates=entity_candidates,
            grounding=grounding,
            chunks=chunks,
            source_catalog=source_catalog,
        )
        payload.update(generation)
        return payload

    def _answer_with_release_gate(
        self,
        *,
        query: str,
        payload: dict[str, Any],
        entity_candidates: list[dict[str, Any]],
        grounding: dict[str, Any],
        chunks: list[dict[str, Any]],
        source_catalog: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if not llm_available():
            return {
                "answer": "",
                "answer_verification": {
                    "release_ready": False,
                    "verifier_used": False,
                    "reason": "LLM 未配置",
                },
                "answer_release_ready": False,
            }

        answer_text = self._generate_grounded_answer(
            query=query,
            payload=payload,
            entity_candidates=entity_candidates,
            grounding=grounding,
            chunks=chunks,
            source_catalog=source_catalog,
        )
        verification = self._verify_answer(
            query=query,
            payload=payload,
            answer_text=answer_text,
            source_catalog=source_catalog,
            chunks=chunks,
        )

        repair_attempts = 0
        while (
            settings.llm_verifier_enabled
            and not verification.get("release_ready", False)
            and repair_attempts < settings.llm_answer_repair_attempts
        ):
            repair_attempts += 1
            answer_text = self._repair_answer(
                query=query,
                payload=payload,
                answer_text=answer_text,
                verification=verification,
                source_catalog=source_catalog,
                chunks=chunks,
            )
            verification = self._verify_answer(
                query=query,
                payload=payload,
                answer_text=answer_text,
                source_catalog=source_catalog,
                chunks=chunks,
            )

        cited_source_labels = sorted(set(re.findall(r"\[(S\d+)\]", answer_text)))
        cited_sources = [row for row in source_catalog if row["label"] in cited_source_labels]
        return {
            "answer": answer_text,
            "answer_verification": verification,
            "answer_release_ready": bool(verification.get("release_ready", False)),
            "answer_generation_trace": {
                "repair_attempts": repair_attempts,
                "cited_source_labels": cited_source_labels,
            },
            "answer_sources": cited_sources,
        }

    def _generate_grounded_answer(
        self,
        *,
        query: str,
        payload: dict[str, Any],
        entity_candidates: list[dict[str, Any]],
        grounding: dict[str, Any],
        chunks: list[dict[str, Any]],
        source_catalog: list[dict[str, Any]],
    ) -> str:
        query_type = str(payload.get("query_context", {}).get("query_type") or "")
        query_type_rules = []
        if query_type == "multi_hop_strategy":
            query_type_rules.extend(
                [
                    "本题是多跳策略题；如果证据只支持“候选区域/候选底材/优先考虑”，就不要写成“最高效/最稳妥/唯一正确”。",
                    "若用户问“最高效”，但证据只有怪物密度、候选区域或启发式标签，请明确写“按当前证据可优先考虑”，不要把启发式直接升级为绝对结论。",
                    "关于 build 偏好、底材排序或刷图路线，只能陈述证据明确支持的候选关系。",
                ]
            )
        elif query_type == "numeric_reasoning":
            query_type_rules.extend(
                [
                    "本题是数值题；必须显式写出阈值、变量范围与最终比较过程。",
                    "不要省略查表步骤，不要做线性插值。",
                ]
            )
        else:
            query_type_rules.append("本题是事实题；不要把候选信息升级成未被证据直接支持的强结论。")

        prompt = (
            "问题：\n"
            f"{query}\n\n"
            "Query Understanding：\n"
            f"{json.dumps(payload['retrieval_trace'], ensure_ascii=False, indent=2)}\n\n"
            "排序理由：\n"
            f"{json.dumps(payload['ranking_reasons'], ensure_ascii=False, indent=2)}\n\n"
            "理由摘要：\n"
            f"{payload['reason_summary']}\n\n"
            "数值推理摘要：\n"
            f"{json.dumps(payload['numeric_reasoning_summary'], ensure_ascii=False, indent=2)}\n\n"
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
            "可用引用标签（只能引用这里出现的标签）：\n"
            f"{json.dumps(source_catalog, ensure_ascii=False, indent=2)}\n\n"
            "按题型附加规则：\n"
            f"{json.dumps(query_type_rules, ensure_ascii=False, indent=2)}\n\n"
            "请严格输出中文答案，并遵守以下规则：\n"
            "1. 只允许使用给定证据，不要补造事实。\n"
            "2. 每个关键判断句末都必须附 [Sx] 标签，标签必须来自 source_catalog。\n"
            "3. 数值题必须明确写出阈值/表项/计算过程，不允许线性插值。\n"
            "4. 策略题如果证据不足以支持“最高效/最稳妥/最佳”，必须降级成“按当前证据可优先考虑/候选之一”。\n"
            "5. 如果证据不够，直接写“证据不足”，不要猜。\n"
            "6. 输出格式固定为：\n"
            "【结论】\\n...\n【依据】\\n- ...[Sx]\n【关键来源】\\n- [Sx] 标题 | URL\n"
        )
        return complete_text(
            system_prompt="你是一个严谨的 Diablo II 问答系统回答器。你必须只基于证据作答，并显式引用给定标签。",
            user_prompt=prompt,
            temperature=0.0,
        )

    def _verify_answer(
        self,
        *,
        query: str,
        payload: dict[str, Any],
        answer_text: str,
        source_catalog: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
    ) -> dict[str, Any]:
        fallback = {
            "release_ready": False,
            "citation_gate_passed": False,
            "numeric_gate_passed": False,
            "grounding_gate_passed": False,
            "verifier_used": False,
            "unsupported_claims": [],
            "invalid_citations": [],
            "missing_citation_issues": [],
            "summary": "verifier unavailable",
            "repair_instruction": "请仅保留有证据和引用标签支持的结论。",
        }
        if not settings.llm_verifier_enabled:
            fallback["summary"] = "LLM verifier disabled"
            return fallback
        if not llm_available(api_key=settings.llm_verifier_api_key, base_url=settings.llm_verifier_base_url):
            fallback["summary"] = "LLM verifier not configured"
            return fallback

        verifier_prompt = (
            "你是问答系统的 release gate verifier。请检查 answer 是否严格基于证据，并只返回 JSON。\n"
            "检查项：\n"
            "1. grounding_gate_passed：answer 是否包含未被证据支持的事实。\n"
            "2. citation_gate_passed：关键判断是否带 [Sx] 标签，且标签在 source_catalog 中存在。\n"
            "3. numeric_gate_passed：若是数值题，是否引用了明确阈值/表项/变量来源，且没有线性插值。\n"
            "4. release_ready：以上三个 gate 是否都通过。\n\n"
            "只返回 JSON，格式：\n"
            "{\n"
            '  "release_ready": true,\n'
            '  "citation_gate_passed": true,\n'
            '  "numeric_gate_passed": true,\n'
            '  "grounding_gate_passed": true,\n'
            '  "verifier_used": true,\n'
            '  "unsupported_claims": [],\n'
            '  "invalid_citations": [],\n'
            '  "missing_citation_issues": [],\n'
            '  "summary": "...",\n'
            '  "repair_instruction": "..."\n'
            "}\n\n"
            f"问题：{query}\n\n"
            f"answer_constraints：{json.dumps(payload['retrieval_trace'].get('answer_constraints', {}), ensure_ascii=False, indent=2)}\n\n"
            f"source_catalog：{json.dumps(source_catalog, ensure_ascii=False, indent=2)}\n\n"
            f"evidence_chunks：{json.dumps(chunks[:6], ensure_ascii=False, indent=2)}\n\n"
            f"answer：\n{answer_text}\n"
        )
        verification = complete_json(
            system_prompt="你是严谨的引用校验器，只能返回 JSON。",
            user_prompt=verifier_prompt,
            fallback=fallback,
            model=settings.llm_verifier_model,
            api_key=settings.llm_verifier_api_key,
            base_url=settings.llm_verifier_base_url,
            temperature=0.0,
        )
        verification.setdefault("verifier_used", True)
        verification["release_ready"] = bool(verification.get("release_ready", False))
        verification["citation_gate_passed"] = bool(verification.get("citation_gate_passed", False))
        verification["numeric_gate_passed"] = bool(verification.get("numeric_gate_passed", False))
        verification["grounding_gate_passed"] = bool(verification.get("grounding_gate_passed", False))
        verification.setdefault("unsupported_claims", [])
        verification.setdefault("invalid_citations", [])
        verification.setdefault("missing_citation_issues", [])
        verification.setdefault("summary", "")
        verification.setdefault("repair_instruction", "请删掉无证据内容并补齐合法引用标签。")
        return verification

    def _repair_answer(
        self,
        *,
        query: str,
        payload: dict[str, Any],
        answer_text: str,
        verification: dict[str, Any],
        source_catalog: list[dict[str, Any]],
        chunks: list[dict[str, Any]],
    ) -> str:
        repair_prompt = (
            f"问题：{query}\n\n"
            f"原答案：\n{answer_text}\n\n"
            f"校验问题：\n{json.dumps(verification, ensure_ascii=False, indent=2)}\n\n"
            f"source_catalog：\n{json.dumps(source_catalog, ensure_ascii=False, indent=2)}\n\n"
            f"evidence_chunks：\n{json.dumps(chunks[:6], ensure_ascii=False, indent=2)}\n\n"
            "请修复答案，只保留有证据支持的内容，并补全 [Sx] 标签。\n"
            "若校验指出存在过强措辞（如“最高效”“最稳妥”“优先目标”）但证据只支持候选关系，请主动降级成“按当前证据可优先考虑”“候选之一”。\n"
            "输出格式仍然必须是：\n"
            "【结论】\\n...\n【依据】\\n- ...[Sx]\n【关键来源】\\n- [Sx] 标题 | URL\n"
        )
        return complete_text(
            system_prompt="你是问答答案修复器，只能依据给定 evidence 修复答案。",
            user_prompt=repair_prompt,
            temperature=0.0,
        )

    @staticmethod
    def _build_source_catalog(chunks: list[dict[str, Any]], provenance: list[dict[str, Any]]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        seen_keys: set[tuple[str, str]] = set()

        def add_source(title: str, url: str, source_id: str, authority_tier: str, locator: str) -> None:
            normalized_url = str(url or "").strip()
            normalized_title = str(title or "").strip() or locator
            key = (normalized_url, normalized_title)
            if key in seen_keys:
                return
            seen_keys.add(key)
            sources.append(
                {
                    "label": f"S{len(sources) + 1}",
                    "title": normalized_title,
                    "url": normalized_url,
                    "source_id": source_id,
                    "authority_tier": authority_tier,
                    "locator": locator,
                }
            )

        for row in chunks[:8]:
            metadata = row.get("metadata", {}) or {}
            add_source(
                title=str(metadata.get("title") or row.get("chunk_id") or ""),
                url=str(metadata.get("source") or ""),
                source_id=str(metadata.get("source_id") or ""),
                authority_tier=str(metadata.get("authority_tier") or ""),
                locator=str(row.get("chunk_id") or ""),
            )

        for row in provenance[:8]:
            add_source(
                title=str(row.get("source_id") or row.get("provenance_id") or ""),
                url=str(row.get("evidence_url") or ""),
                source_id=str(row.get("source_id") or ""),
                authority_tier=str(row.get("authority_tier") or ""),
                locator=str(row.get("provenance_id") or ""),
            )

        return sources[:12]

    def _selected_backend_name(self) -> str:
        configured = settings.retrieval_backend.lower().strip()
        if configured == "postgres":
            return "postgres" if self.postgres.available else "local-fallback"
        if configured == "local":
            return "local"
        return "postgres" if self.postgres.available else "local"

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

    def _retrieve_chunks(self, query_context: dict[str, Any], confident_entity_ids: list[str]) -> tuple[list[dict[str, Any]], str]:
        backend = self._selected_backend_name()
        if backend == "postgres":
            try:
                pg_chunks = self.postgres.query_chunks(query_context, top_k=self._target_k(query_context))
                if pg_chunks:
                    return pg_chunks, self._classify_postgres_backend(pg_chunks, self.postgres.last_lane_sources)
            except Exception:
                if settings.retrieval_backend.lower().strip() == "postgres":
                    raise
            return self._retrieve_chunks_local(query_context, confident_entity_ids), "local-fallback"
        return self._retrieve_chunks_local(query_context, confident_entity_ids), backend

    @staticmethod
    def _classify_postgres_backend(chunks: list[dict[str, Any]], lane_sources: list[str] | None = None) -> str:
        sources = set(lane_sources or [])
        if not sources:
            sources = {str(row.get("retrieval_source") or "") for row in chunks}
        if 'postgres_bm25' in sources and 'postgres_vector' in sources:
            return 'postgres-hybrid'
        if 'postgres_bm25' in sources:
            return 'postgres-bm25'
        if 'postgres_vector' in sources:
            return 'postgres-vector'
        if 'postgres' in sources:
            return 'postgres-lexical'
        return 'postgres'

    def _retrieve_chunks_local(
        self,
        query_context: dict[str, Any],
        confident_entity_ids: list[str],
    ) -> list[dict[str, Any]]:
        combined: dict[str, dict[str, Any]] = {}
        rewrite_candidates = [row for row in query_context.get("rewrite_candidates", []) if row.get("accepted")]
        if not rewrite_candidates:
            rewrite_candidates = [query_context.get("accepted_rewrite") or {"rewrite_text": query_context.get("expanded_query", "")}]

        top_k = self._target_k(query_context)

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
    def _target_k(query_context: dict[str, Any]) -> int:
        top_k = 8
        for lane in query_context.get("retrieval_plan", []):
            top_k = max(top_k, int(lane.get("target_k") or 0))
        return top_k

    @staticmethod
    def _structured_evidence_weight(query_type: str, support_key: str) -> float:
        if query_type == 'numeric_reasoning':
            mapping = {'breakpoints': 8.5, 'rules': 8.2, 'runewords': 7.2, 'monster_resistances': 7.8}
            return mapping.get(support_key, 6.0)
        if query_type == 'multi_hop_strategy':
            mapping = {'runewords': 7.6, 'areas': 7.2, 'skills': 7.0, 'base_items': 7.0}
            return mapping.get(support_key, 5.8)
        mapping = {'monster_resistances': 7.0, 'unique_items': 6.5, 'areas': 6.2, 'skills': 6.0}
        return mapping.get(support_key, 5.5)

    def _build_structured_evidence_chunks(self, query_context: dict[str, Any]) -> list[dict[str, Any]]:
        query_type = str(query_context.get('query_type') or 'fact_lookup')
        support = query_context.get('structured_support', {}) or {}
        rows: list[dict[str, Any]] = []
        for support_key, items in support.items():
            for idx, item in enumerate(items[:3], start=1):
                if not self._structured_item_matches_query(query_context, item):
                    continue
                title = str(item.get('name') or item.get('entity') or item.get('description') or support_key)
                text = json.dumps(item, ensure_ascii=False)
                rows.append({
                    'chunk_id': f'structured::{support_key}::{idx}::{title[:40]}',
                    'text': text,
                    'metadata': {
                        'doc_id': f'structured::{support_key}',
                        'source_id': 'structured-support',
                        'source': item.get('source_url') or item.get('source') or 'docs/tier0/structured',
                        'title': f'{support_key}::{title}',
                        'authority_tier': 'structured_db',
                    },
                    'distance': None,
                    'score': self._structured_evidence_weight(query_type, support_key),
                    'retrieval_source': 'structured_support',
                    'source_set': ['structured_support'],
                    'fused_score': self._structured_evidence_weight(query_type, support_key),
                })
        return rows

    @staticmethod
    def _structured_item_matches_query(query_context: dict[str, Any], item: dict[str, Any]) -> bool:
        query_text = " ".join(
            [
                str(query_context.get("original_query") or ""),
                str(query_context.get("expanded_query") or ""),
            ]
        ).lower()
        if not query_text.strip():
            return True
        candidate_fields = [
            item.get("name"),
            item.get("name_zh"),
            item.get("entity"),
            item.get("description"),
        ]
        for value in candidate_fields:
            text = str(value or "").strip()
            if not text:
                continue
            lowered = text.lower()
            if len(lowered) >= 4 and lowered in query_text:
                return True
            if re.search(r"[\u4e00-\u9fff]", text) and text in query_text:
                return True
        return False

    def _merge_structured_evidence(self, query_context: dict[str, Any], chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        structured_rows = self._build_structured_evidence_chunks(query_context)
        combined: dict[str, dict[str, Any]] = {row['chunk_id']: row for row in structured_rows}
        for row in chunks:
            row['fused_score'] = self._score_chunk_for_query(row, query_context)
            existing = combined.get(row['chunk_id'])
            if existing is None or float(row.get('fused_score', row.get('score', 0.0))) > float(existing.get('fused_score', existing.get('score', 0.0))):
                combined[row['chunk_id']] = row
        ordered = list(combined.values())
        ordered.sort(key=lambda row: (-float(row.get('fused_score', row.get('score', 0.0))), str(row.get('chunk_id', ''))))
        return ordered[:8]

    @staticmethod
    def _score_chunk_for_query(row: dict[str, Any], query_context: dict[str, Any]) -> float:
        metadata = row.get('metadata', {}) or {}
        title = str(metadata.get('title') or '').lower()
        text = str(row.get('text') or row.get('content') or '').lower()
        source_id = str(metadata.get('source_id') or '')
        retrieval_source = str(row.get('retrieval_source') or '')
        preferred_source_ids = set(query_context.get('preferred_source_ids', []) or [])
        preferred_title_contains = [str(x).lower() for x in (query_context.get('preferred_title_contains') or [])]
        preferred_text_contains = [str(x).lower() for x in (query_context.get('preferred_text_contains') or [])]
        canonical_hints = [str(x).lower() for x in (query_context.get('canonical_hints') or [])]
        preferred_terms = [str(x).lower() for x in (query_context.get('preferred_terms') or [])]

        score = 0.0
        score += {
            'entity_link': 9.0,
            'structured_support': 8.5,
            'postgres_bm25': 7.0,
            'postgres': 6.5,
            'lexical': 6.0,
            'postgres_vector': 4.0,
            'vector': 3.5,
        }.get(retrieval_source, 2.5)
        if source_id in preferred_source_ids:
            score += 4.0
        if any(token in title for token in preferred_title_contains):
            score += 8.0
        if any(token in text for token in preferred_text_contains):
            score += 6.0
        if any(token and token in title for token in preferred_terms):
            score += 5.0
        if any(token and token in text for token in preferred_terms):
            score += 3.0
        if any(token and token in title for token in canonical_hints):
            score += 6.0
        if any(token and token in text for token in canonical_hints):
            score += 4.0
        if source_id == 'curated-anchor' and 'curated-anchor' not in preferred_source_ids:
            score -= 3.0
        return round(score, 4)

    @staticmethod
    def _dedupe_structured_support(support: dict[str, Any]) -> dict[str, Any]:
        deduped: dict[str, Any] = {}
        for key, items in (support or {}).items():
            seen: set[str] = set()
            kept: list[dict[str, Any]] = []
            for item in items or []:
                marker = json.dumps(item, ensure_ascii=False, sort_keys=True)
                if marker in seen:
                    continue
                seen.add(marker)
                kept.append(item)
            deduped[key] = kept
        return deduped

    @staticmethod
    def _dedupe_ranking_reasons(reasons: list[dict[str, Any]]) -> list[dict[str, Any]]:
        deduped: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for row in reasons:
            key = (str(row.get('chunk_id') or ''), str(row.get('title') or ''))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    def _build_ranking_reasons(self, query_context: dict[str, Any], chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        reasons: list[dict[str, Any]] = []
        query_type = str(query_context.get('query_type') or 'fact_lookup')
        strategy_reason_map = {
            'runewords::Enigma': '核心装备关系：该问题涉及谜团，优先展示符文之语本体。',
            'areas::The Secret Cow Level': '刷图场景关系：牛场常作为高密度刷底材区域。',
            'areas::Ancient Tunnels': '刷图场景关系：古代通道是高价值场景候选之一。',
            'areas::Pit Level 1': '刷图场景关系：地穴是常见高价值刷图路线。',
            'base_items::Mage Plate': '底材关系：Mage Plate 是谜团的低力量需求热门底材。',
            'base_items::Dusk Shroud': '底材关系：Dusk Shroud 是谜团常见轻甲底材。',
            'base_items::Archon Plate': '底材关系：Archon Plate 是高防谜团热门底材。',
            'breakpoints::Sorceress': '断点关系：法师 FCR 档位表是该数值问题的核心依据。',
            'breakpoints::Sorceress (Lightning / Chain Lightning)': '断点关系：电系法师施法档位与通用法师不同，需优先查看专用表。',
            'rules::rules': '规则关系：数值问题必须优先受规则表约束，避免幻觉插值。',
            'monster_resistances::Mephisto': '抗性关系：该问题直接询问劳模/墨菲斯托的抗性数据。',
        }
        for row in chunks[:8]:
            title = str(row.get('metadata', {}).get('title') or '')
            source_set = list(row.get('source_set', []))
            lane_reason = []
            if row.get('retrieval_source') == 'structured_support':
                lane_reason.append('结构化证据优先')
            if 'postgres_bm25' in source_set or row.get('retrieval_source') == 'postgres_bm25':
                lane_reason.append('BM25 命中强')
            if 'postgres_vector' in source_set or row.get('retrieval_source') == 'postgres_vector':
                lane_reason.append('向量语义相近')
            if 'postgres' in source_set or row.get('retrieval_source') == 'postgres':
                lane_reason.append('词面/约束命中')
            if row.get('metadata', {}).get('source_id') == 'curated-anchor':
                lane_reason.append('社区锚点卡优先')

            strategy_reason = None
            for key, value in strategy_reason_map.items():
                if key in title:
                    strategy_reason = value
                    break
            if strategy_reason is None and query_type == 'multi_hop_strategy' and row.get('metadata', {}).get('source_id') == 'curated-anchor':
                strategy_reason = '构筑锚点关系：用于稳定 build 名称与核心玩法检索。'
            if strategy_reason is None and query_type == 'numeric_reasoning' and row.get('metadata', {}).get('source_id') == 'curated-anchor':
                strategy_reason = '装备锚点关系：用于稳定变量来源与数值问题检索。'

            reasons.append({
                'chunk_id': row.get('chunk_id'),
                'title': title,
                'retrieval_source': row.get('retrieval_source'),
                'source_set': source_set,
                'fused_score': row.get('fused_score', row.get('score')),
                'lane_reason': lane_reason,
                'strategy_reason': strategy_reason,
            })
        return reasons

    def _build_reason_summary(self, query_context: dict[str, Any], ranking_reasons: list[dict[str, Any]]) -> str:
        query_type = str(query_context.get('query_type') or 'fact_lookup')
        lines = []
        if query_type == 'numeric_reasoning':
            lines.append('本题是数值判断题，优先依据断点表、规则约束和变量来源。')
        elif query_type == 'multi_hop_strategy':
            lines.append('本题是多跳策略题，优先依据构筑、核心装备、底材候选与刷图场景关系。')
        else:
            lines.append('本题是事实查询题，优先依据结构化事实、锚点卡和高权重文本证据。')

        seen = set()
        for row in ranking_reasons[:5]:
            title = str(row.get('title') or '')
            lane_reason = '；'.join(row.get('lane_reason', []))
            strategy_reason = row.get('strategy_reason') or ''
            parts = [part for part in [lane_reason, strategy_reason] if part]
            key = (title, tuple(parts))
            if not title or not parts or key in seen:
                continue
            seen.add(key)
            lines.append(f'- {title}: ' + '；'.join(parts))
        return '\n'.join(lines)

    def _build_numeric_reasoning_summary(self, query_context: dict[str, Any]) -> dict[str, Any]:
        if str(query_context.get('query_type')) != 'numeric_reasoning':
            return {}

        query = str(query_context.get('original_query') or '')
        support = query_context.get('structured_support', {}) or {}
        numbers = [int(value) for value in re.findall(r'\d+', query)]
        current_value = numbers[0] if numbers else None
        stat = 'FCR' if 'fcr' in query.lower() or '施法' in query else ('FHR' if 'fhr' in query.lower() else ('FBR' if 'fbr' in query.lower() else None))
        breakpoints = support.get('breakpoints', [])
        runewords = support.get('runewords', [])

        addition_ranges = []
        for runeword in runewords:
            for mod in runeword.get('modifiers', []):
                code = str(mod.get('code') or '')
                if stat == 'FCR' and code == 'cast3':
                    addition_ranges.append({'source': runeword.get('name'), 'min': mod.get('min'), 'max': mod.get('max')})
                if stat == 'FHR' and code == 'balance3':
                    addition_ranges.append({'source': runeword.get('name'), 'min': mod.get('min'), 'max': mod.get('max')})

        scenarios = []
        if current_value is not None and breakpoints:
            for table in breakpoints[:2]:
                values = sorted(int(point['value']) for point in table.get('breakpoints', []) if point.get('value') is not None)
                next_breakpoint = next((value for value in values if value > current_value), None)
                for addition in addition_ranges[:1] or [{'source': None, 'min': None, 'max': None}]:
                    min_total = current_value + int(addition['min']) if addition.get('min') is not None else current_value
                    max_total = current_value + int(addition['max']) if addition.get('max') is not None else current_value
                    scenarios.append({
                        'table': table.get('entity'),
                        'category': table.get('category'),
                        'current_value': current_value,
                        'next_breakpoint': next_breakpoint,
                        'source': addition.get('source'),
                        'min_total': min_total,
                        'max_total': max_total,
                        'crosses_next_breakpoint': bool(next_breakpoint is not None and max_total >= next_breakpoint),
                    })
        return {
            'stat': stat,
            'current_value': current_value,
            'addition_ranges': addition_ranges,
            'scenarios': scenarios,
        }

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
