from __future__ import annotations

import unittest

from crawler.extractors import extract_page_fields
from crawler.selection import normalize_urls, slug_url


class NormalizeUrlsTests(unittest.TestCase):
    def test_normalize_urls_deduplicates_and_removes_fragments(self) -> None:
        urls = [
            " https://example.com/a#top ",
            "https://example.com/a",
            "//example.com/b",
            "",
        ]
        self.assertEqual(normalize_urls(urls), ["https://example.com/a", "https://example.com/b"])

    def test_slug_url_keeps_query_signal(self) -> None:
        self.assertEqual(slug_url("http://bbs.diablo2.com.cn/read.php?tid=239897"), "bbs.diablo2.com.cn-read.php__tid-239897")


class HtmlExtractionTests(unittest.TestCase):
    def test_extract_page_fields_strips_noise_and_keeps_title(self) -> None:
        html = b"""
        <html>
          <head>
            <title>Sample Title</title>
            <style>.hidden { display:none; }</style>
          </head>
          <body>
            <h1>Heading</h1>
            <script>window.alert('ignore');</script>
            <p>Useful text</p>
          </body>
        </html>
        """
        title, text = extract_page_fields(html, "text/html; charset=utf-8", ("utf-8",))
        self.assertEqual(title, "Sample Title")
        self.assertIn("Heading", text)
        self.assertIn("Useful text", text)
        self.assertNotIn("ignore", text)


if __name__ == "__main__":
    unittest.main()
