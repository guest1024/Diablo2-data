#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Mozilla/5.0 (compatible; Diablo2KnowledgeBot/1.0; +https://example.invalid/bot)"


class HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignore_depth = 0
        self._inside_title = False
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style", "noscript"}:
            self._ignore_depth += 1
        elif lowered == "title":
            self._inside_title = True
        elif lowered in {"p", "br", "li", "div", "section", "article", "tr", "table", "h1", "h2", "h3", "h4"}:
            self._text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in {"script", "style", "noscript"} and self._ignore_depth:
            self._ignore_depth -= 1
        elif lowered == "title":
            self._inside_title = False
        elif lowered in {"p", "br", "li", "div", "section", "article", "tr", "table", "h1", "h2", "h3", "h4"}:
            self._text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignore_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._inside_title:
            self._title_parts.append(text)
        self._text_parts.append(text)

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    @property
    def text(self) -> str:
        text = " ".join(self._text_parts)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()


@dataclass
class PageRecord:
    source_id: str
    url: str
    local_path: str
    title: str
    chars: int
    sha256: str
    status: str = "ok"
    note: str | None = None


def split_chunks(text: str, max_chars: int = 1200) -> list[str]:
    paragraphs = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if not paragraphs:
        return []
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
            continue
        start = 0
        while start < len(paragraph):
            chunks.append(paragraph[start : start + max_chars])
            start += max_chars
        current = ""
    if current:
        chunks.append(current)
    return chunks


def fetch(url: str, timeout: int) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_html(html: bytes) -> tuple[str, str]:
    parser = HtmlTextExtractor()
    parser.feed(html.decode("utf-8", "ignore"))
    return parser.title or "", parser.text


def select_diablo2io(inventory: list[str]) -> list[str]:
    quotas = {
        "runewords": 24,
        "uniques": 70,
        "sets": 24,
        "skills": 28,
        "monsters": 20,
        "areas": 18,
        "recipes": 16,
        "npcs": 6,
        "quests": 8,
        "base": 24,
    }
    selected: list[str] = []
    for category, quota in quotas.items():
        matches = [
            url
            for url in inventory
            if f"diablo2.io/{category}/" in url and url.endswith(".html")
        ]
        selected.extend(matches[:quota])
    return selected


def select_arreat(inventory: list[str]) -> list[str]:
    patterns = [
        ("/classes/", 7),
        ("/skills/", 24),
        ("/items/", 30),
        ("/monsters/", 18),
        ("/quests/", 10),
        ("/maps/", 6),
    ]
    selected: list[str] = []
    for fragment, quota in patterns:
        matches = [
            url
            for url in inventory
            if fragment in url and url.endswith(".shtml")
        ]
        selected.extend(matches[:quota])
    return selected


def slug(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/") or "root"
    return path.replace("/", "__")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch higher-value Diablo II detail pages from current inventories")
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--output-root", default="docs/tier0/high-value")
    args = parser.parse_args()

    output_root = ROOT / args.output_root
    raw_root = output_root / "raw"
    normalized_root = output_root / "normalized"
    derived_root = output_root / "derived"
    raw_root.mkdir(parents=True, exist_ok=True)
    normalized_root.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)

    diablo2io_inventory = (ROOT / "docs/tier0/url-inventories/diablo2-io.txt").read_text(encoding="utf-8").splitlines()
    arreat_inventory = (ROOT / "docs/tier0/url-inventories/arreat-summit.txt").read_text(encoding="utf-8").splitlines()

    targets = {
        "diablo2-io": select_diablo2io(diablo2io_inventory),
        "arreat-summit": select_arreat(arreat_inventory),
    }

    docs = []
    chunks = []
    records: list[PageRecord] = []
    for source_id, urls in targets.items():
        for url in urls:
            local = raw_root / source_id / f"{slug(url)}.html"
            local.parent.mkdir(parents=True, exist_ok=True)
            try:
                if local.exists() and local.stat().st_size > 64:
                    content = local.read_bytes()
                else:
                    content = fetch(url, args.timeout)
                    local.write_bytes(content)
                title, text = parse_html(content)
                sha = hashlib.sha256(content).hexdigest()
                record = PageRecord(source_id=source_id, url=url, local_path=str(local.relative_to(ROOT)), title=title, chars=len(text), sha256=sha)
                records.append(record)
                doc_id = hashlib.sha256(f"{source_id}|{url}".encode()).hexdigest()[:24]
                docs.append(
                    {
                        "doc_id": doc_id,
                        "source_id": source_id,
                        "source_url": url,
                        "local_path": str(local.relative_to(ROOT)),
                        "title": title,
                        "text": text,
                        "char_count": len(text),
                    }
                )
                for idx, chunk in enumerate(split_chunks(text), start=1):
                    chunks.append(
                        {
                            "chunk_id": f"{doc_id}::chunk-{idx}",
                            "doc_id": doc_id,
                            "source_id": source_id,
                            "source_url": url,
                            "title": title,
                            "chunk_index": idx,
                            "char_count": len(chunk),
                            "text": chunk,
                        }
                    )
            except (TimeoutError, URLError, HTTPError, Exception) as exc:  # noqa: BLE001
                local.write_text(repr(exc), encoding="utf-8")
                records.append(
                    PageRecord(
                        source_id=source_id,
                        url=url,
                        local_path=str(local.relative_to(ROOT)),
                        title="",
                        chars=0,
                        sha256="",
                        status="error",
                        note=repr(exc),
                    )
                )

    (normalized_root / "documents.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in docs) + "\n", encoding="utf-8")
    (derived_root / "chunks.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in chunks) + "\n", encoding="utf-8")

    by_source = defaultdict(lambda: {"pages": 0, "chars": 0, "chunks": 0})
    for rec in records:
        by_source[rec.source_id]["pages"] += 1
        by_source[rec.source_id]["chars"] += rec.chars
    for ch in chunks:
        by_source[ch["source_id"]]["chunks"] += 1

    manifest = {
        "sources": dict(by_source),
        "page_count": len(records),
        "chunk_count": len(chunks),
        "documents_path": str((normalized_root / "documents.jsonl").relative_to(ROOT)),
        "chunks_path": str((derived_root / "chunks.jsonl").relative_to(ROOT)),
        "pages": [record.__dict__ for record in records],
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Tier 0 High-Value Content Expansion",
        "",
        f"- Pages fetched: `{len(records)}`",
        f"- Chunks generated: `{len(chunks)}`",
        "",
        "| Source | Pages | Chars | Chunks |",
        "| --- | ---: | ---: | ---: |",
    ]
    for source_id, stats in sorted(by_source.items()):
        lines.append(f"| {source_id} | {stats['pages']} | {stats['chars']} | {stats['chunks']} |")
    (output_root / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
