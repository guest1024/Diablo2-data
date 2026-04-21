#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "docs/tier0/next-data-acquisition-priority.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(FILE.is_file(), "next acquisition priority doc exists")
    text = FILE.read_text(encoding="utf-8")
    for phrase in [
        "91D2",
        "TTBN",
        "diablo2.io",
        "Arreat Summit",
        "PureDiablo D2Wiki",
        "Build / FAQ / Route 结构化",
        "关系增强",
        "推荐执行顺序",
        "成功标准",
    ]:
        expect(phrase in text, f"priority doc contains '{phrase}'")
    print("PASS: next acquisition priority verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
