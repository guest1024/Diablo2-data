#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/tier0/bilingual-graphrag-guidelines.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(GUIDE.is_file(), "bilingual GraphRAG guidelines exist")
    text = GUIDE.read_text(encoding="utf-8")
    for phrase in [
        "实体主键语言无关",
        "Alias 比 embedding 更重要",
        "Chunk 不要只按长度切",
        "Embedding 要分“实体检索”和“证据检索”",
        "Graph 里最值得先建的节点",
        "Graph 里最值得先建的边",
        "版本和语言必须进排序",
        "中英文混合问答的推荐流程",
    ]:
        expect(phrase in text, f"guidelines contain '{phrase}'")
    print("PASS: bilingual guidelines verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
