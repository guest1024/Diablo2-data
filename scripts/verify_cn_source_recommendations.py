#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "docs/tier0/cn-source-recommendations.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(FILE.is_file(), "cn source recommendations exists")
    text = FILE.read_text(encoding="utf-8")
    for phrase in [
        "91d2.cn",
        "ttbn.cn",
        "diablo2.com.cn",
        "第一优先级",
        "建议抓取方向",
        "并入策略",
    ]:
        expect(phrase in text, f"recommendations contain '{phrase}'")
    print("PASS: cn source recommendations verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
