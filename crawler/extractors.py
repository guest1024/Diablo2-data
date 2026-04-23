from __future__ import annotations

import re
from html.parser import HTMLParser

from crawler.http_client import decode_bytes


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


class TextExtractor(HTMLParser):
    block_tags = {"p", "div", "section", "article", "li", "br", "h1", "h2", "h3", "h4", "h5", "h6"}
    ignore_tags = {"script", "style", "noscript"}

    def __init__(self) -> None:
        super().__init__()
        self._ignore_depth = 0
        self._in_title = False
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        name = tag.lower()
        if name in self.ignore_tags:
            self._ignore_depth += 1
        elif name == "title":
            self._in_title = True
        elif name in self.block_tags:
            self._text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        name = tag.lower()
        if name in self.ignore_tags and self._ignore_depth:
            self._ignore_depth -= 1
        elif name == "title":
            self._in_title = False
        elif name in self.block_tags:
            self._text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignore_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._title_parts)).strip()

    @property
    def text(self) -> str:
        text = " ".join(self._text_parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()


def extract_page_fields(body: bytes, content_type: str | None, encoding_hints: tuple[str, ...]) -> tuple[str, str]:
    text = decode_bytes(body, content_type, encoding_hints)
    if "html" not in (content_type or "").lower():
        return "", text.strip()
    parser = TextExtractor()
    parser.feed(text)
    return parser.title, parser.text
