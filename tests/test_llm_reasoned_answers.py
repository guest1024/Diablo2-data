from __future__ import annotations

import os
import unittest

from tests.support.llm_case_graph import build_case_graph


class LLMReasonedAnswersTest(unittest.TestCase):
    def test_llm_reasoned_answers(self) -> None:
        graph = build_case_graph()
        cases = [
            ("地狱劳模火抗多少？", ["75", "Mephisto"]),
        ]
        if os.environ.get("RUN_SLOW_LLM_TESTS", "").strip().lower() in {"1", "true", "yes", "on"}:
            cases.extend(
                [
                    ("我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？", ["105", "Spirit", "117"]),
                    ("我想玩锤丁，谜团底材去哪里刷最高效？", ["Mage Plate", "The Secret Cow Level", "Enigma"]),
                ]
            )
        for query, markers in cases:
            with self.subTest(query=query):
                attempts = 3 if os.environ.get("RUN_SLOW_LLM_TESTS", "").strip().lower() in {"1", "true", "yes", "on"} else 2
                last_failures: list[str] = []
                for _ in range(attempts):
                    state = graph.invoke({"query": query, "markers": markers, "failures": []})
                    last_failures = list(state.get("failures", []))
                    if not last_failures:
                        break
                self.assertFalse(last_failures, msg="\n".join(last_failures))


if __name__ == "__main__":
    unittest.main()
