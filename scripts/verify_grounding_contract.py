#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    chroma_dir = ROOT / ".data/chroma"
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
    chroma_dir.mkdir(parents=True, exist_ok=True)

    service = Diablo2QAService()
    service.ingest()

    spirit = service.answer("精神符文之语是什么？", use_llm=False)
    expect(spirit["grounding_mode"] == "graph+evidence", "Spirit keeps graph grounding")
    expect(bool(spirit["grounding_entity_ids"]), "Spirit exposes grounding entity ids")
    expect(all(row["subject_id"] in set(spirit["grounding_entity_ids"]) for row in spirit["claims"]), "Spirit claims stay inside grounding entity ids")
    expect(bool(spirit["sources"]), "Spirit returns source URLs")
    expect(bool(spirit["evidence_chunks"]), "Spirit returns evidence chunks")

    for query, expected_title in {
        "乔丹是什么？": "Stone of Jordan / 乔丹（Curated Anchor Card）",
        "无限是什么？": "Infinity / 无限（Curated Anchor Card）",
        "橡树之心是什么？": "Heart of the Oak / HOTO（Curated Anchor Card）",
    }.items():
        body = service.answer(query, use_llm=False)
        expect(body["grounding_mode"] == "curated-evidence", f"{query} falls back to curated evidence grounding")
        expect(body["grounding_entity_ids"] == [], f"{query} does not expose noisy graph grounding ids")
        expect(body["claims"] == [], f"{query} suppresses unrelated graph claims")
        expect(body["provenance"] == [], f"{query} suppresses unrelated graph provenance")
        expect(bool(body["sources"]), f"{query} still returns source URLs")
        expect(body["evidence_chunks"][0]["title"] == expected_title, f"{query} top evidence chunk is the curated anchor")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
