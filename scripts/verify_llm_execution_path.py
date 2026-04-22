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
    body = service.answer("精神盾底材是什么", use_llm=True)

    expect(bool(body.get("answer")), "LLM execution path returns an answer payload")
    expect(body["query_analysis"]["intent"] == "crafting_base", "LLM execution path preserves query analysis")
    if body.get("llm_error"):
        expect("外部 LLM 不可用" in body["answer"], "LLM failure falls back to grounded answer")
    else:
        expect("来源" in body["answer"] or "URL" in body["answer"], "LLM answer still cites sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
