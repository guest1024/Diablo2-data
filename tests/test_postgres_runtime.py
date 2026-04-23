from __future__ import annotations

import unittest

from tests.support.harness import assert_known_backend, make_service, maybe_run_psql


class PostgresRuntimeTest(unittest.TestCase):
    def test_postgres_runtime_ready(self) -> None:
        service = make_service()
        status = service.runtime_status()
        self.assertIn("postgres", status)
        self.assertIn("retrieval_backend", status)
        assert_known_backend(self, status["retrieval_backend"])
        self.assertTrue(status["postgres"].get("available"))
        self.assertTrue(status["postgres"].get("bm25_runtime"))
        self.assertTrue(status["postgres"].get("vector_runtime"))

        ok, output = maybe_run_psql("SELECT current_database();")
        if ok:
            self.assertTrue(output)
            checks = {
                "pg_trgm": "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm');",
                "vector": "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector');",
                "pg_textsearch": "SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_textsearch');",
                "d2.chunks": "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='d2' AND table_name='chunks');",
                "d2.canonical_claims": "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='d2' AND table_name='canonical_claims');",
                "d2.provenance": "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='d2' AND table_name='provenance');",
                "embedding column": "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema='d2' AND table_name='chunks' AND column_name='embedding');",
            }
            for label, sql in checks.items():
                with self.subTest(label=label):
                    ok, output = maybe_run_psql(sql)
                    self.assertTrue(ok, msg=output)
                    self.assertIn(output, {"t", "true", "True"})

            ok, output = maybe_run_psql("SELECT COUNT(*) FROM pg_indexes WHERE schemaname='d2' AND indexname IN ('d2_chunks_bm25_text_idx','d2_chunks_bm25_title_idx');")
            self.assertTrue(ok, msg=output)
            self.assertGreaterEqual(int(output or "0"), 2)

        body = service.answer("劳模掉不掉军帽？", use_llm=False)
        self.assertIn(body["retrieval_backend"], {"postgres", "postgres-lexical", "postgres-bm25", "postgres-vector", "postgres-hybrid"})


if __name__ == "__main__":
    unittest.main()
