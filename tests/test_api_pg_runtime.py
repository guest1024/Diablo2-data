from __future__ import annotations

import unittest

from tests.support.harness import make_test_client


class ApiPostgresRuntimeTest(unittest.TestCase):
    def test_api_pg_runtime(self) -> None:
        client = make_test_client()

        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        body = health.json()
        self.assertTrue(body.get("ok"))
        self.assertEqual(body.get("retrieval_backend"), "postgres")
        self.assertTrue(body.get("postgres", {}).get("available"))
        self.assertTrue(body.get("postgres", {}).get("bm25_runtime"))
        self.assertTrue(body.get("postgres", {}).get("vector_runtime"))

        cases = [
            ("劳模掉不掉军帽？", "fact_lookup"),
            ("我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？", "numeric_reasoning"),
            ("我想玩锤丁，谜团底材去哪里刷最高效？", "multi_hop_strategy"),
        ]
        for query, expected_type in cases:
            with self.subTest(query=query):
                response = client.post("/qa", json={"query": query, "use_llm": False})
                self.assertEqual(response.status_code, 200)
                body = response.json()
                self.assertIn(body.get("retrieval_backend"), {"postgres-hybrid", "postgres-bm25", "postgres-lexical", "postgres-vector"})
                self.assertEqual(body.get("query_context", {}).get("query_type"), expected_type)
                self.assertTrue(body.get("chunks"))
                self.assertTrue(body.get("ranking_reasons"))
                self.assertTrue(body.get("reason_summary"))
                self.assertTrue(body.get("answer_source_catalog"))
                self.assertIn("lane_reason", body["ranking_reasons"][0])
                self.assertEqual(body["retrieval_trace"]["actual_backend"], body["retrieval_backend"])


if __name__ == "__main__":
    unittest.main()
