from __future__ import annotations

import unittest

from tests.support.harness import assert_known_backend, make_service


class QueryExecutionChainTest(unittest.TestCase):
    def test_query_execution_chain(self) -> None:
        service = make_service()
        status = service.runtime_status()
        self.assertIn("retrieval_backend", status)
        assert_known_backend(self, status["retrieval_backend"])

        cases = [
            ("劳模掉不掉军帽？", "fact_lookup", False),
            ("我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？", "numeric_reasoning", True),
            ("我想玩锤丁，谜团底材去哪里刷最高效？", "multi_hop_strategy", True),
        ]
        for query, expected_type, expect_subplan in cases:
            with self.subTest(query=query):
                body = service.answer(query, use_llm=False)
                trace = body["retrieval_trace"]
                self.assertEqual(trace["query_type"], expected_type)
                self.assertTrue(trace["accepted_rewrite"]["rewrite_text"])
                self.assertTrue(trace["rewrite_candidates"])
                self.assertTrue(body["chunks"])
                self.assertTrue(body["resolved_entities"])
                self.assertTrue(body["structured_support"])
                self.assertTrue(body["answer_source_catalog"])
                assert_known_backend(self, body["retrieval_backend"])
                self.assertEqual(bool(trace["subquestion_plan"]), expect_subplan)


if __name__ == "__main__":
    unittest.main()
