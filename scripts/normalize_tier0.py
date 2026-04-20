#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import uuid
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignore_depth = 0
        self._title_parts: list[str] = []
        self._text_parts: list[str] = []
        self._inside_title = False

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
class NormalizedDoc:
    doc_id: str
    source_id: str
    source_name: str
    label: str
    source_url: str
    local_path: str
    content_type: str | None
    authority_tier: str
    lane: str
    title: str
    text: str
    discovered_url_count: int
    discovered_url_sample: list[str]
    note: str | None


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


def normalize_content(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".html":
        parser = HtmlTextExtractor()
        parser.feed(raw)
        title = parser.title or path.stem
        return title, parser.text
    if suffix in {".json"}:
        try:
            payload = json.loads(raw)
            text = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        except json.JSONDecodeError:
            text = raw
        return path.stem, text.strip()
    return path.stem, raw.strip()


def load_registry(path: Path) -> dict[str, dict]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    return {source["id"]: source for source in registry["sources"]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Tier 0 raw captures into GraphRAG-friendly docs/chunks")
    parser.add_argument("--manifest", default="docs/tier0/fetch-manifest.json")
    parser.add_argument("--registry", default="docs/tier0/source-registry.json")
    parser.add_argument("--output-root", default="docs/tier0")
    args = parser.parse_args()

    manifest_path = ROOT / args.manifest
    registry_path = ROOT / args.registry
    output_root = ROOT / args.output_root

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registry = load_registry(registry_path)

    normalized_dir = output_root / "normalized"
    derived_dir = output_root / "derived"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    derived_dir.mkdir(parents=True, exist_ok=True)

    docs: list[NormalizedDoc] = []
    chunks: list[dict] = []

    for entry in manifest["results"]:
        local_path = ROOT / entry["output_path"]
        title, text = normalize_content(local_path)
        source = registry[entry["source_id"]]
        doc = NormalizedDoc(
            doc_id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{entry['source_id']}::{entry['label']}::{entry['url']}")),
            source_id=entry["source_id"],
            source_name=source["name"],
            label=entry["label"],
            source_url=entry["url"],
            local_path=entry["output_path"],
            content_type=entry.get("content_type"),
            authority_tier="official" if source["lane"] == "official" else ("structured_db" if source["lane"] in {"structured_db", "open_data", "api"} else source["lane"]),
            lane=source["lane"],
            title=title,
            text=text,
            discovered_url_count=entry["discovered_url_count"],
            discovered_url_sample=entry["discovered_url_sample"],
            note=entry.get("note"),
        )
        docs.append(doc)
        for index, chunk_text in enumerate(split_chunks(text), start=1):
            chunks.append(
                {
                    "chunk_id": f"{doc.doc_id}::chunk-{index}",
                    "doc_id": doc.doc_id,
                    "source_id": doc.source_id,
                    "source_name": doc.source_name,
                    "source_url": doc.source_url,
                    "label": doc.label,
                    "title": doc.title,
                    "lane": doc.lane,
                    "authority_tier": doc.authority_tier,
                    "chunk_index": index,
                    "text": chunk_text,
                    "char_count": len(chunk_text),
                }
            )

    docs_path = normalized_dir / "documents.jsonl"
    chunks_path = derived_dir / "chunks.jsonl"
    docs_path.write_text(
        "\n".join(json.dumps(doc.__dict__, ensure_ascii=False) for doc in docs) + "\n",
        encoding="utf-8",
    )
    chunks_path.write_text(
        "\n".join(json.dumps(chunk, ensure_ascii=False) for chunk in chunks) + "\n",
        encoding="utf-8",
    )

    docs_by_source = Counter(doc.source_id for doc in docs)
    chunks_by_source = Counter(chunk["source_id"] for chunk in chunks)
    summary = {
        "document_count": len(docs),
        "chunk_count": len(chunks),
        "sources": sorted({doc.source_id for doc in docs}),
        "documents_by_source": dict(docs_by_source),
        "chunks_by_source": dict(chunks_by_source),
        "documents_path": str(docs_path.relative_to(ROOT)),
        "chunks_path": str(chunks_path.relative_to(ROOT)),
    }
    (output_root / "normalized-manifest.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_root / "normalized-report.md").write_text(
        "# Tier 0 Normalization Report\n\n"
        f"- Documents: `{len(docs)}`\n"
        f"- Chunks: `{len(chunks)}`\n"
        f"- Sources: `{', '.join(summary['sources'])}`\n"
        f"- Documents file: `{summary['documents_path']}`\n"
        f"- Chunks file: `{summary['chunks_path']}`\n\n"
        "## Per-source counts\n\n"
        "| Source | Documents | Chunks |\n"
        "| --- | ---: | ---: |\n"
        + "\n".join(
            f"| {source} | {docs_by_source[source]} | {chunks_by_source[source]} |"
            for source in summary["sources"]
        )
        + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
