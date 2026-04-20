#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "Mozilla/5.0 (compatible; Diablo2KnowledgeBot/1.0; +https://example.invalid/bot)"

TARGETS = [
    "https://www.purediablo.com/d2wiki/Horadric_Cube",
    "https://www.purediablo.com/d2wiki/Runewords",
    "https://www.purediablo.com/d2wiki/Unique_Items",
    "https://www.purediablo.com/d2wiki/Amazon",
    "https://www.purediablo.com/d2wiki/Amazon_Skills",
    "https://www.purediablo.com/d2wiki/Amazon_Bow_and_Crossbow",
    "https://www.purediablo.com/d2wiki/Amazon_Passive_and_Magic",
    "https://www.purediablo.com/d2wiki/Amazon_Javelin_and_Spear",
    "https://www.purediablo.com/d2wiki/Barbarian",
    "https://www.purediablo.com/d2wiki/Barbarian_Skills",
    "https://www.purediablo.com/d2wiki/Barbarian_Combat_Skills",
    "https://www.purediablo.com/d2wiki/Barbarian_Combat_Masteries",
    "https://www.purediablo.com/d2wiki/Barbarian_Warcries",
    "https://www.purediablo.com/d2wiki/Assassin",
    "https://www.purediablo.com/d2wiki/Assassin_Skills",
    "https://www.purediablo.com/d2wiki/Assassin_Shadow_Disciplines",
    "https://www.purediablo.com/d2wiki/Assassin_Martial_Arts",
    "https://www.purediablo.com/d2wiki/Assassin_Traps",
    "https://www.purediablo.com/d2wiki/Paladin",
    "https://www.purediablo.com/d2wiki/Paladin_Skills",
    "https://www.purediablo.com/d2wiki/Paladin_Combat_Skills",
    "https://www.purediablo.com/d2wiki/Paladin_Offensive_Auras",
    "https://www.purediablo.com/d2wiki/Paladin_Defensive_Auras",
    "https://www.purediablo.com/d2wiki/Sorceress",
    "https://www.purediablo.com/d2wiki/Sorceress_Skills",
    "https://www.purediablo.com/d2wiki/Sorceress_Cold_Spells",
    "https://www.purediablo.com/d2wiki/Sorceress_Fire_Spells",
    "https://www.purediablo.com/d2wiki/Sorceress_Lightning_Spells",
    "https://www.purediablo.com/d2wiki/Druid",
    "https://www.purediablo.com/d2wiki/Druid_Skills",
    "https://www.purediablo.com/d2wiki/Druid_Elemental_Skills",
    "https://www.purediablo.com/d2wiki/Druid_Summoning_Skills",
    "https://www.purediablo.com/d2wiki/Druid_Shapeshifting_Skills",
    "https://www.purediablo.com/d2wiki/Necromancer",
    "https://www.purediablo.com/d2wiki/Necromancer_Skills",
    "https://www.purediablo.com/d2wiki/Necromancer_Poison_and_Bone",
    "https://www.purediablo.com/d2wiki/Necromancer_Items",
    "https://www.purediablo.com/d2wiki/Runes",
    "https://www.purediablo.com/d2wiki/Set_Items",
    "https://www.purediablo.com/d2wiki/Mercenaries",
    "https://www.purediablo.com/d2wiki/Magic_Find",
    "https://www.purediablo.com/d2wiki/Act_I",
    "https://www.purediablo.com/d2wiki/Act_II",
    "https://www.purediablo.com/d2wiki/Act_III",
    "https://www.purediablo.com/d2wiki/Act_IV",
    "https://www.purediablo.com/d2wiki/Act_V",
    "https://www.purediablo.com/d2wiki/Diablo_II_Manual",
    "https://www.purediablo.com/d2wiki/Trang-Oul%27s_Avatar",
    "https://www.purediablo.com/d2wiki/V1.10_FAQ",
]


class HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignore = 0
        self._title = []
        self._text = []
        self._in_title = False

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
    def title(self):
        return " ".join(self._title).strip()

    @property
    def text(self):
        text = " ".join(self._text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
        return text.strip()


def split_chunks(text: str, max_chars: int = 1200) -> list[str]:
    parts = [part.strip() for part in re.split(r"\n{2,}", text) if part.strip()]
    if not parts:
        return []
    chunks = []
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
                chunks.append(part[i:i + max_chars])
            current = ""
    if current:
        chunks.append(current)
    return chunks


def slug(url: str) -> str:
    return url.rstrip("/").split("/")[-1].replace("%27", "'").replace("/", "_")


def fetch(url: str, timeout: int) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--output-root", default="docs/tier0/purediablo-high-value")
    args = parser.parse_args()

    out = ROOT / args.output_root
    raw = out / "raw"
    normalized = out / "normalized"
    derived = out / "derived"
    raw.mkdir(parents=True, exist_ok=True)
    normalized.mkdir(parents=True, exist_ok=True)
    derived.mkdir(parents=True, exist_ok=True)

    docs = []
    chunks = []
    pages = []
    for url in TARGETS:
        file_slug = slug(url)
        raw_path = raw / f"{file_slug}.html"
        try:
            if raw_path.exists() and raw_path.stat().st_size > 64:
                html = raw_path.read_bytes()
            else:
                html = fetch(url, args.timeout)
                raw_path.write_bytes(html)
            parser_ = HtmlTextExtractor()
            parser_.feed(html.decode("utf-8", "ignore"))
            title = parser_.title
            text = parser_.text
            doc_id = hashlib.sha256(url.encode()).hexdigest()[:24]
            docs.append({
                "doc_id": doc_id,
                "source_id": "purediablo-d2wiki",
                "source_url": url,
                "local_path": str(raw_path.relative_to(ROOT)),
                "title": title,
                "text": text,
                "char_count": len(text),
            })
            for idx, chunk in enumerate(split_chunks(text), start=1):
                chunks.append({
                    "chunk_id": f"{doc_id}::chunk-{idx}",
                    "doc_id": doc_id,
                    "source_id": "purediablo-d2wiki",
                    "source_url": url,
                    "title": title,
                    "chunk_index": idx,
                    "char_count": len(chunk),
                    "text": chunk,
                })
            pages.append({
                "url": url,
                "title": title,
                "chars": len(text),
                "sha256": hashlib.sha256(html).hexdigest(),
                "status": "ok",
            })
        except (HTTPError, URLError, TimeoutError, Exception) as exc:  # noqa: BLE001
            raw_path.write_text(repr(exc), encoding="utf-8")
            pages.append({
                "url": url,
                "title": "",
                "chars": 0,
                "sha256": "",
                "status": "error",
                "note": repr(exc),
            })

    (normalized / "documents.jsonl").write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in docs) + "\n", encoding="utf-8")
    (derived / "chunks.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks) + "\n", encoding="utf-8")
    manifest = {
        "page_count": len(pages),
        "successful_pages": sum(1 for page in pages if page.get("status") == "ok"),
        "chunk_count": len(chunks),
        "char_count": sum(p["chars"] for p in pages),
        "pages": pages,
        "documents_path": str((normalized / "documents.jsonl").relative_to(ROOT)),
        "chunks_path": str((derived / "chunks.jsonl").relative_to(ROOT)),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "README.md").write_text(
        "# PureDiablo D2Wiki High-Value Corpus\n\n"
        f"- Pages: `{manifest['page_count']}`\n"
        f"- Chunks: `{manifest['chunk_count']}`\n"
        f"- Chars: `{manifest['char_count']}`\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
