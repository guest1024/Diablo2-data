#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def check_doc(path_str: str, markers: list[str]) -> None:
    path = ROOT / path_str
    expect(path.is_file(), f"{path_str} exists")
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        expect(marker in text, f"{path_str} contains marker: {marker}")


def main() -> int:
    check_doc(
        "docs/知识文档管理手册.md",
        [
            "文档分层",
            "总览层",
            "方案层",
            "数据层",
            "验证层",
        ],
    )
    check_doc(
        "docs/RAG开发手册.md",
        [
            "当前数据层总览",
            "merged 主知识层",
            "chroma-ready 包",
            "curated anchor 层",
            "当前已经能解决哪些问题",
            "当前还不够强的地方",
        ],
    )
    check_doc(
        "docs/用户使用手册.md",
        [
            "快速启动",
            "可以怎么问",
            "回答结果怎么理解",
            "当前系统擅长什么",
            "当前能力边界",
        ],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
