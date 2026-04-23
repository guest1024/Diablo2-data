from __future__ import annotations

import unittest

from crawler.models import SourceConfig
from crawler.relevance import is_relevant_page


class RelevanceTests(unittest.TestCase):
    def test_trade_page_is_filtered(self) -> None:
        source = SourceConfig.from_dict(
            {
                "id": "demo",
                "label": "Demo",
                "enabled": True,
                "weight": 1,
                "region": "CN",
                "transport": "direct",
                "observed_on": "2026-04-23",
                "observed_status": "ok",
                "home_url": "https://example.com/",
            }
        )
        relevant, reason = is_relevant_page(source, "https://example.com/post/1", "暗黑2卖号说明", "这是一个卖号帖")
        self.assertFalse(relevant)
        self.assertEqual(reason, "excluded-by-title-keyword")

    def test_strategy_article_is_kept(self) -> None:
        source = SourceConfig.from_dict(
            {
                "id": "demo",
                "label": "Demo",
                "enabled": True,
                "weight": 1,
                "region": "CN",
                "transport": "direct",
                "observed_on": "2026-04-23",
                "observed_status": "ok",
                "home_url": "https://example.com/",
            }
        )
        relevant, reason = is_relevant_page(source, "https://example.com/build/1", "冰法开荒攻略", "讲解暗黑2开荒和mf玩法")
        self.assertTrue(relevant)
        self.assertIsNone(reason)


if __name__ == "__main__":
    unittest.main()
