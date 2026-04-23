from __future__ import annotations

import json
from collections import defaultdict
from contextlib import contextmanager
from typing import Any, Iterator

from .config import settings
from .chroma_store import HashingEmbeddingFunction


class PostgresRetrievalStore:
    def __init__(self, database_url: str | None = None) -> None:
        self.database_url = database_url or settings.database_url
        self.driver_name: str | None = None
        self.driver = self._import_driver()
        self.embedding = HashingEmbeddingFunction()
        self._vector_available: bool | None = None
        self._bm25_available: bool | None = None
        self.last_lane_sources: list[str] = []

    def _import_driver(self) -> Any | None:
        try:
            import psycopg  # type: ignore

            self.driver_name = "psycopg"
            return psycopg
        except Exception:
            try:
                import psycopg2  # type: ignore

                self.driver_name = "psycopg2"
                return psycopg2
            except Exception:
                self.driver_name = None
                return None

    @property
    def available(self) -> bool:
        return bool(self.database_url and self.driver is not None)

    @contextmanager
    def connection(self) -> Iterator[Any]:
        if not self.available:
            raise RuntimeError("postgres retrieval store is not available")
        conn = self.driver.connect(self.database_url)  # type: ignore[call-arg]
        try:
            yield conn
        finally:
            conn.close()

    def _fetchall(self, sql: str, params: tuple[Any, ...] | list[Any]) -> list[dict[str, Any]]:
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            cols = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()
        return [self._normalize_row(dict(zip(cols, row))) for row in rows]

    @staticmethod
    def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
        for key, value in list(row.items()):
            if isinstance(value, str):
                stripped = value.strip()
                if stripped.startswith("{") or stripped.startswith("["):
                    try:
                        row[key] = json.loads(value)
                    except Exception:
                        pass
        return row

    @staticmethod
    def _quote_literal(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    def health(self) -> dict[str, Any]:
        if not self.available:
            return {"available": False, "driver": self.driver_name, "database_url_configured": bool(self.database_url)}
        try:
            rows = self._fetchall("SELECT current_database() AS current_database, current_schema() AS current_schema", ())
            row = rows[0] if rows else {}
            return {
                "available": True,
                "driver": self.driver_name,
                "database_url_configured": True,
                "vector_runtime": self.supports_vector_runtime(),
                "bm25_runtime": self.supports_bm25_runtime(),
                **row,
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "available": False,
                "driver": self.driver_name,
                "database_url_configured": True,
                "error": str(exc),
            }

    def _resolve_pg_entities(self, query_context: dict[str, Any], limit: int = 6) -> list[dict[str, Any]]:
        search_terms = list(dict.fromkeys(
            [str(query_context.get("normalized_query") or "")]
            + [str(term) for term in query_context.get("canonical_hints", []) if term]
            + [str(term) for term in query_context.get("preferred_terms", []) if term]
        ))
        rows: dict[str, dict[str, Any]] = {}
        sql = """
            SELECT
                entity_type,
                entity_id,
                name,
                name_zh,
                GREATEST(similarity(name, %s), similarity(COALESCE(name_zh, ''), %s)) AS sim
            FROM d2.entity_catalog
            WHERE name %% %s OR COALESCE(name_zh, '') %% %s
               OR lower(name) LIKE '%%' || lower(%s) || '%%'
               OR lower(COALESCE(name_zh, '')) LIKE '%%' || lower(%s) || '%%'
            ORDER BY sim DESC, name
            LIMIT %s
        """
        for term in search_terms[:6]:
            if not term.strip():
                continue
            try:
                for row in self._fetchall(sql, (term, term, term, term, term, term, limit)):
                    entity_id = str(row.get("entity_id"))
                    if entity_id not in rows or float(row.get("sim", 0.0)) > float(rows[entity_id].get("sim", 0.0)):
                        rows[entity_id] = row
            except Exception:
                continue
        ordered = list(rows.values())
        ordered.sort(key=lambda row: (-float(row.get("sim", 0.0)), str(row.get("name", ""))))
        return ordered[:limit]

    def _graph_expansion_terms(self, pg_entities: list[dict[str, Any]], limit: int = 8) -> list[str]:
        if not pg_entities:
            return []
        entity_ids = [str(row["entity_id"]) for row in pg_entities[:4]]
        sql = """
            WITH catalog AS (
                SELECT entity_id AS object_id, name FROM d2.entity_catalog
                UNION ALL
                SELECT object_id, name FROM d2.strategy_object_catalog
            )
            SELECT DISTINCT ec.name AS object_name
            FROM (
                SELECT subject_id, object_id FROM d2.gameplay_edges
                UNION ALL
                SELECT subject_id, object_id FROM d2.strategy_edge_facts
                UNION ALL
                SELECT subject_id, object_id FROM d2.strategy_edges
            ) ge
            JOIN catalog ec ON ec.object_id = ge.object_id
            WHERE ge.subject_id = ANY(%s)
            ORDER BY ec.name
            LIMIT %s
        """
        try:
            rows = self._fetchall(sql, (entity_ids, limit))
        except Exception:
            return []
        return [str(row.get("object_name")) for row in rows if row.get("object_name")]

    def _rule_terms(self, query_context: dict[str, Any], limit: int = 6) -> list[str]:
        query_type = str(query_context.get("query_type") or "")
        sql = """
            SELECT canonical_subject, description
            FROM dict.rule_dictionary
            WHERE active = TRUE
              AND (
                lower(rule_type) LIKE '%%' || lower(%s) || '%%'
                OR lower(subject_type) LIKE '%%' || lower(%s) || '%%'
              )
            ORDER BY confidence DESC NULLS LAST, canonical_subject
            LIMIT %s
        """
        try:
            rows = self._fetchall(sql, (query_type, query_type, limit))
        except Exception:
            return []
        terms: list[str] = []
        for row in rows:
            if row.get("canonical_subject"):
                terms.append(str(row["canonical_subject"]))
            if row.get("description") and len(terms) < limit:
                terms.append(str(row["description"]))
        return terms[:limit]

    def supports_bm25_runtime(self) -> bool:
        if self._bm25_available is not None:
            return self._bm25_available
        if not self.available:
            self._bm25_available = False
            return self._bm25_available
        sql = """
            SELECT 1
            FROM pg_extension
            WHERE extname = 'pg_textsearch'
            LIMIT 1
        """
        try:
            rows = self._fetchall(sql, ())
            self._bm25_available = bool(rows)
        except Exception:
            self._bm25_available = False
        return self._bm25_available

    def supports_vector_runtime(self) -> bool:
        if self._vector_available is not None:
            return self._vector_available
        if not self.available:
            self._vector_available = False
            return self._vector_available
        sql = """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'd2'
              AND table_name = 'chunks'
              AND column_name = 'embedding'
            LIMIT 1
        """
        try:
            rows = self._fetchall(sql, ())
            self._vector_available = bool(rows)
        except Exception:
            self._vector_available = False
        return self._vector_available

    def _lane_weight_map(self, query_type: str) -> dict[str, float]:
        if query_type == 'fact_lookup':
            return {
                'postgres_bm25': 3.0,
                'postgres': 2.2,
                'postgres_vector': 0.8,
            }
        if query_type == 'numeric_reasoning':
            return {
                'postgres_bm25': 1.6,
                'postgres': 2.6,
                'postgres_vector': 0.7,
            }
        if query_type == 'multi_hop_strategy':
            return {
                'postgres_bm25': 2.2,
                'postgres': 1.8,
                'postgres_vector': 1.2,
            }
        return {
            'postgres_bm25': 2.0,
            'postgres': 2.0,
            'postgres_vector': 1.0,
        }

    @staticmethod
    def _source_bonus(source_id: str, authority_tier: str, query_type: str) -> float:
        source_id = source_id or ''
        authority_tier = authority_tier or ''
        bonus = 0.0
        if source_id == 'curated-anchor':
            bonus += 4.5 if query_type == 'fact_lookup' else (3.5 if query_type == 'numeric_reasoning' else 2.5)
        if authority_tier == 'curated':
            bonus += 2.0
        if authority_tier == 'official':
            bonus += 1.2
        if authority_tier == 'structured_db':
            bonus += 1.0
        return bonus

    def _bm25_query(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        if not self.supports_bm25_runtime():
            return []
        literal = self._quote_literal(query_text)
        sql = f"""
            SELECT
                chunk_id,
                doc_id,
                source_id,
                source_url,
                title,
                authority_tier,
                text_content,
                metadata
            FROM d2.chunks
            ORDER BY text_content <@> {literal} ASC
            LIMIT {int(top_k)}
        """
        try:
            rows = self._fetchall(sql, ())
        except Exception:
            return []
        normalized_rows = []
        total = max(len(rows), 1)
        for idx, row in enumerate(rows, start=1):
            normalized_rows.append({
                'chunk_id': row['chunk_id'],
                'text': row['text_content'],
                'metadata': {
                    **(row.get('metadata') if isinstance(row.get('metadata'), dict) else {}),
                    'doc_id': row.get('doc_id'),
                    'source_id': row.get('source_id'),
                    'source': row.get('source_url'),
                    'title': row.get('title'),
                    'authority_tier': row.get('authority_tier'),
                },
                'distance': None,
                'score': round(float(total - idx + 1), 6),
                'retrieval_source': 'postgres_bm25',
            })
        return normalized_rows

    def _vector_query(self, query_text: str, top_k: int) -> list[dict[str, Any]]:
        if not self.supports_vector_runtime():
            return []
        query_vector = self.embedding.embed_query(query_text)
        vector_value = '[' + ','.join(f'{value:.8f}' for value in query_vector) + ']'
        sql = """
            SELECT chunk_id, doc_id, source_id, source_url, title, authority_tier, text_content, metadata,
                   ROUND((1 - (embedding <=> %s::vector))::numeric, 6) AS vector_score
            FROM d2.chunks
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        try:
            rows = self._fetchall(sql, (vector_value, vector_value, top_k))
        except Exception:
            return []
        return [{
            'chunk_id': row['chunk_id'],
            'text': row['text_content'],
            'metadata': {
                **(row.get('metadata') if isinstance(row.get('metadata'), dict) else {}),
                'doc_id': row.get('doc_id'),
                'source_id': row.get('source_id'),
                'source': row.get('source_url'),
                'title': row.get('title'),
                'authority_tier': row.get('authority_tier'),
            },
            'distance': None,
            'score': float(row.get('vector_score', 0.0)),
            'retrieval_source': 'postgres_vector',
        } for row in rows]

    def get_grounding(self, canonical_ids: list[str], limit_claims: int = 6, limit_provenance: int = 6) -> dict[str, Any]:
        if not self.available or not canonical_ids:
            return {"claims": [], "provenance": []}
        claims_sql = """
            SELECT canonical_claim_id, subject_id, subject_type, subject_name, subject_aliases, predicate, predicate_family,
                   object_value, supporting_sources, supporting_source_count, claim_variant_count, metadata
            FROM d2.canonical_claims
            WHERE subject_id = ANY(%s)
            ORDER BY supporting_source_count DESC NULLS LAST, canonical_claim_id
            LIMIT %s
        """
        provenance_sql = """
            SELECT provenance_id, claim_id, subject_id, predicate, source_id, evidence_doc_id, evidence_url, authority_tier, lane, metadata
            FROM d2.provenance
            WHERE subject_id = ANY(%s)
            ORDER BY provenance_id
            LIMIT %s
        """
        try:
            claims = self._fetchall(claims_sql, (canonical_ids, limit_claims))
            provenance = self._fetchall(provenance_sql, (canonical_ids, limit_provenance))
        except Exception:
            return {"claims": [], "provenance": []}
        return {"claims": claims, "provenance": provenance}

    def query_chunks(self, query_context: dict[str, Any], top_k: int = 8) -> list[dict[str, Any]]:
        self.last_lane_sources = []
        if not self.available:
            return []

        query_type = str(query_context.get('query_type') or 'fact_lookup')
        weights = self._lane_weight_map(query_type)
        rrf_k = 60.0

        normalized_query = str(query_context.get("normalized_query") or query_context.get("expanded_query") or "").strip()
        rewrite = str((query_context.get("accepted_rewrite") or {}).get("rewrite_text") or query_context.get("expanded_query") or normalized_query).strip()
        if not rewrite:
            return []

        pg_entities = self._resolve_pg_entities(query_context)
        graph_terms = self._graph_expansion_terms(pg_entities)
        rule_terms = self._rule_terms(query_context)
        preferred_terms = list(dict.fromkeys(
            [str(term) for term in query_context.get("preferred_terms", []) if term] + graph_terms + rule_terms
        ))[:12]
        preferred_sources = [str(term) for term in query_context.get("preferred_source_ids", []) if term][:12]
        discouraged_sources = [str(term) for term in query_context.get("discouraged_source_ids", []) if term][:12]

        sql = """
            WITH chunk_scores AS (
                SELECT
                    c.chunk_id,
                    c.doc_id,
                    c.source_id,
                    c.source_url,
                    c.title,
                    c.authority_tier,
                    c.text_content,
                    c.metadata,
                    GREATEST(similarity(c.title, %s), similarity(c.text_content, %s)) AS trigram_score,
                    CASE WHEN lower(c.title) LIKE '%%' || lower(%s) || '%%' THEN 3.0 ELSE 0.0 END AS title_bonus,
                    CASE WHEN lower(c.text_content) LIKE '%%' || lower(%s) || '%%' THEN 1.5 ELSE 0.0 END AS text_bonus,
                    CASE WHEN array_length(%s::text[], 1) IS NOT NULL AND c.source_id = ANY(%s::text[]) THEN 3.0 ELSE 0.0 END AS preferred_source_bonus,
                    CASE WHEN array_length(%s::text[], 1) IS NOT NULL AND c.source_id = ANY(%s::text[]) THEN -5.0 ELSE 0.0 END AS discouraged_source_penalty,
                    COALESCE((
                        SELECT SUM(
                            CASE
                                WHEN lower(c.title) LIKE '%%' || lower(term) || '%%' THEN 2.5
                                WHEN lower(c.text_content) LIKE '%%' || lower(term) || '%%' THEN 1.5
                                ELSE 0.0
                            END
                        )
                        FROM unnest(%s::text[]) AS term
                    ), 0.0) AS preferred_terms_bonus
                FROM d2.chunks c
                WHERE c.title %% %s
                   OR c.text_content %% %s
                   OR lower(c.title) LIKE '%%' || lower(%s) || '%%'
                   OR lower(c.text_content) LIKE '%%' || lower(%s) || '%%'
                   OR EXISTS (
                        SELECT 1
                        FROM unnest(%s::text[]) AS term
                        WHERE lower(c.title) LIKE '%%' || lower(term) || '%%'
                           OR lower(c.text_content) LIKE '%%' || lower(term) || '%%'
                   )
            )
            SELECT *,
                ROUND((trigram_score * 4.0 + title_bonus + text_bonus + preferred_source_bonus + discouraged_source_penalty + preferred_terms_bonus)::numeric, 4) AS final_score
            FROM chunk_scores
            ORDER BY final_score DESC, chunk_id
            LIMIT %s
        """
        rows = self._fetchall(
            sql,
            (
                rewrite,
                rewrite,
                normalized_query,
                normalized_query,
                preferred_sources,
                preferred_sources,
                discouraged_sources,
                discouraged_sources,
                preferred_terms,
                rewrite,
                rewrite,
                normalized_query,
                normalized_query,
                preferred_terms,
                top_k,
            ),
        )
        lexical_rows = [
            {
                "chunk_id": row["chunk_id"],
                "text": row["text_content"],
                "metadata": {
                    **(row.get("metadata") if isinstance(row.get("metadata"), dict) else {}),
                    "doc_id": row.get("doc_id"),
                    "source_id": row.get("source_id"),
                    "source": row.get("source_url"),
                    "title": row.get("title"),
                    "authority_tier": row.get("authority_tier"),
                },
                "distance": None,
                "score": float(row.get("final_score", 0.0)),
                "retrieval_source": "postgres",
                "graph_terms": graph_terms,
                "rule_terms": rule_terms,
            }
            for row in rows
        ]

        lane_rows = {
            'postgres': lexical_rows,
            'postgres_bm25': self._bm25_query(rewrite, top_k=top_k),
            'postgres_vector': self._vector_query(rewrite, top_k=top_k),
        }
        lane_presence = {lane for lane, rows_ in lane_rows.items() if rows_}
        self.last_lane_sources = sorted(lane_presence)

        aggregated: dict[str, dict[str, Any]] = {}
        lane_ranks: dict[str, dict[str, int]] = {}
        for lane_name, rows_ in lane_rows.items():
            lane_ranks[lane_name] = {row['chunk_id']: idx for idx, row in enumerate(rows_, start=1)}
            for row in rows_:
                chunk_id = row['chunk_id']
                if chunk_id not in aggregated:
                    aggregated[chunk_id] = {
                        **row,
                        'source_set': [],
                        'lane_scores': {},
                        'fused_score': 0.0,
                    }
                source_set = set(aggregated[chunk_id].get('source_set', []))
                source_set.add(lane_name)
                aggregated[chunk_id]['source_set'] = sorted(source_set)
                aggregated[chunk_id]['lane_scores'][lane_name] = float(row.get('score', 0.0))
                if float(row.get('score', 0.0)) > float(aggregated[chunk_id].get('score', 0.0)):
                    preserved = aggregated[chunk_id].get('source_set', [])
                    lane_scores = aggregated[chunk_id].get('lane_scores', {})
                    fused_score = aggregated[chunk_id].get('fused_score', 0.0)
                    aggregated[chunk_id].update(row)
                    aggregated[chunk_id]['source_set'] = preserved
                    aggregated[chunk_id]['lane_scores'] = lane_scores
                    aggregated[chunk_id]['fused_score'] = fused_score

        for chunk_id, row in aggregated.items():
            fused = 0.0
            for lane_name, rank_map in lane_ranks.items():
                rank = rank_map.get(chunk_id)
                if rank is None:
                    continue
                fused += weights.get(lane_name, 1.0) * (1.0 / (rrf_k + rank))
            source_id = str(row.get('metadata', {}).get('source_id') or '')
            authority_tier = str(row.get('metadata', {}).get('authority_tier') or '')
            fused += self._source_bonus(source_id, authority_tier, query_type)
            row['fused_score'] = round(fused, 8)

        priority = {'postgres_bm25': 0, 'postgres_vector': 1, 'postgres': 2}
        ordered = list(aggregated.values())
        ordered.sort(
            key=lambda item: (
                -float(item.get('fused_score', 0.0)),
                priority.get(str(item.get('retrieval_source')), 9),
                -float(item.get('score', 0.0)),
                str(item.get('chunk_id', '')),
            )
        )
        return ordered[:top_k]
