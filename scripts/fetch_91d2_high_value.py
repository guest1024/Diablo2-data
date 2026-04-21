#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Mozilla/5.0 (compatible; Diablo2KnowledgeBot/1.0; +https://example.invalid/bot)"

CATEGORY_URLS = [
    "https://www.91d2.cn/fq/",
    "https://www.91d2.cn/jichuzhishi/",
    "https://www.91d2.cn/jiaosezhiye/",
    "https://www.91d2.cn/mofajineng/",
    "https://www.91d2.cn/yaomoguiguai/",
    "https://www.91d2.cn/jingyanxinde/",
    "https://www.91d2.cn/changjingditu/",
    "https://www.91d2.cn/xinshouzhiyin/",
    "https://www.91d2.cn/changjianwenti/",
    "https://www.91d2.cn/renwugonglue/",
    "https://www.91d2.cn/wupinzhuangbei/",
]


class HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignore = 0
        self._in_title = False
        self._title: list[str] = []
        self._text: list[str] = []

    def handle_starttag(self, tag, attrs):
        t = tag.lower()
        if t in {"script", "style", "noscript"}:
            self._ignore += 1
        elif t == "title":
            self._in_title = True
        elif t in {"p", "br", "li", "div", "section", "article", "h1", "h2", "h3", "h4"}:
            self._text.append("\n")

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in {"script", "style", "noscript"} and self._ignore:
            self._ignore -= 1
        elif t == "title":
            self._in_title = False
        elif t in {"p", "br", "li", "div", "section", "article", "h1", "h2", "h3", "h4"}:
            self._text.append("\n")

    def handle_data(self, data):
        if self._ignore:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self._title.append(text)
        self._text.append(text)

    @property
    def title(self) -> str:
        return " ".join(self._title).strip()

    @property
    def text(self) -> str:
        text = " ".join(self._text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()


def split_chunks(text: str, max_chars: int = 1200) -> list[str]:
    parts = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if not parts:
        return []
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = part if not current else f"{current}\n\n{part}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(part) <= max_chars:
            current = part
        else:
            for i in range(0, len(part), max_chars):
                chunks.append(part[i : i + max_chars])
            current = ""
    if current:
        chunks.append(current)
    return chunks


def slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1]


def fetch_text(url: str, timeout: int) -> str:
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    r.raise_for_status()
    r.encoding = r.apparent_encoding or "gb2312"
    return r.text


def discover_articles(category_url: str, timeout: int) -> list[str]:
    text = fetch_text(category_url, timeout)
    links = []
    for href in re.findall(r'href=["\']([^"\']+)["\']', text, re.I):
        full = urljoin(category_url, href)
        if "91d2.cn" not in full:
            continue
        if not re.search(r"/\d{4}-\d{2}-\d{2}/\d+\.html$", full):
            continue
        if full not in links:
            links.append(full)
    return links


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch 91d2 high-value Chinese pages")
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--per-category", type=int, default=8)
    parser.add_argument("--output-root", default="docs/tier0/91d2-high-value")
    args = parser.parse_args()

    output_root = ROOT / args.output_root
    raw_root = output_root / "raw"
    normalized_root = output_root / "normalized"
    derived_root = output_root / "derived"
    raw_root.mkdir(parents=True, exist_ok=True)
    normalized_root.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)

    selected_urls = []
    for category in CATEGORY_URLS:
        selected_urls.extend(discover_articles(category, args.timeout)[: args.per_category])

    deduped_urls = []
    seen = set()
    for url in selected_urls:
        if url in seen:
            continue
        seen.add(url)
        deduped_urls.append(url)

    documents = []
    chunks = []
    pages = []
    stats_by_category = defaultdict(lambda: {"pages": 0, "chars": 0, "chunks": 0})

    for url in deduped_urls:
        html = fetch_text(url, args.timeout)
        rel_category = url.split("/")[3]
        raw_path = raw_root / rel_category / f"{slug(url)}.html"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(html, encoding="utf-8")

        parser_ = HtmlTextExtractor()
        parser_.feed(html)
        title = parser_.title
        text = parser_.text

        doc_id = hashlib.sha256(url.encode()).hexdigest()[:24]
        documents.append(
            {
                "doc_id": doc_id,
                "source_id": "91d2",
                "source_url": url,
                "local_path": str(raw_path.relative_to(ROOT)),
                "title": title,
                "text": text,
                "char_count": len(text),
                "language": "zh",
            }
        )

        page_chunks = split_chunks(text)
        for idx, chunk in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "chunk_id": f"{doc_id}::chunk-{idx}",
                    "doc_id": doc_id,
                    "source_id": "91d2",
                    "source_url": url,
                    "title": title,
                    "chunk_index": idx,
                    "char_count": len(chunk),
                    "text": chunk,
                    "language": "zh",
                }
            )

        pages.append(
            {
                "url": url,
                "category": rel_category,
                "title": title,
                "chars": len(text),
                "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
                "chunk_count": len(page_chunks),
            }
        )
        stats = stats_by_category[rel_category]
        stats["pages"] += 1
        stats["chars"] += len(text)
        stats["chunks"] += len(page_chunks)

    (normalized_root / "documents.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in documents) + "\n",
        encoding="utf-8",
    )
    (derived_root / "chunks.jsonl").write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in chunks) + "\n",
        encoding="utf-8",
    )

    manifest = {
        "page_count": len(pages),
        "successful_pages": len(pages),
        "chunk_count": len(chunks),
        "char_count": sum(page["chars"] for page in pages),
        "pages": pages,
        "by_category": dict(stats_by_category),
        "documents_path": str((normalized_root / "documents.jsonl").relative_to(ROOT)),
        "chunks_path": str((derived_root / "chunks.jsonl").relative_to(ROOT)),
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output_root / "README.md").write_text(
        "# 91D2 中文高价值语料\n\n"
        f"- Pages: `{manifest['page_count']}`\n"
        f"- Chunks: `{manifest['chunk_count']}`\n"
        f"- Chars: `{manifest['char_count']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
