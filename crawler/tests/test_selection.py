from __future__ import annotations

import unittest

from crawler.models import FetchResponse, SourceConfig
from crawler.selection import discover_urls, select_candidates


class DiscoverUrlsTests(unittest.TestCase):
    def test_discover_urls_filters_by_rule(self) -> None:
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
                "home_url": "https://www.91d2.cn/",
                "discovery": {
                    "same_host": True,
                    "include": [r"https://www\.91d2\.cn/.+/\d+\.html$"],
                    "exclude": [r"/tag/"],
                },
            }
        )
        html = b'<a href="https://www.91d2.cn/xinshou/100.html">ok</a><a href="https://www.91d2.cn/tag/abc">skip</a>'
        response = FetchResponse(url=source.home_url, status=200, content_type="text/html", body=html)
        self.assertEqual(discover_urls(source, source.home_url, response, max_discover=10), ["https://www.91d2.cn/xinshou/100.html"])


class CandidateSelectionTests(unittest.TestCase):
    def test_curated_urls_rank_before_discovered_urls(self) -> None:
        source = SourceConfig.from_dict(
            {
                "id": "bbs",
                "label": "BBS",
                "enabled": True,
                "weight": 1,
                "region": "CN",
                "transport": "direct",
                "observed_on": "2026-04-23",
                "observed_status": "ok",
                "home_url": "http://bbs.example.com/",
                "robots_url": None,
                "curated_urls": ["http://bbs.example.com/read.php?tid=1"],
                "selection": {"preferred_keywords": ["faq"]},
            }
        )
        discovered = [
            "http://bbs.example.com/read.php?tid=2&tag=faq",
            "http://bbs.example.com/read.php?tid=3",
        ]
        self.assertEqual(select_candidates(source, discovered, limit=2)[0], "http://bbs.example.com/read.php?tid=1")

    def test_denied_keywords_push_urls_down(self) -> None:
        source = SourceConfig.from_dict(
            {
                "id": "guide",
                "label": "Guide",
                "enabled": True,
                "weight": 1,
                "region": "CN",
                "transport": "direct",
                "observed_on": "2026-04-23",
                "observed_status": "ok",
                "home_url": "https://example.com/",
                "robots_url": None,
                "selection": {"preferred_keywords": ["guide"], "denied_keywords": ["trade"]},
            }
        )
        discovered = [
            "https://example.com/guide/trade-post",
            "https://example.com/guide/starter-build",
        ]
        self.assertEqual(select_candidates(source, discovered, limit=1)[0], "https://example.com/guide/starter-build")


if __name__ == "__main__":
    unittest.main()
