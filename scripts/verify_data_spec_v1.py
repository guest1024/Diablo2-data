#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/data-spec-v1.md"


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    expect(SPEC.is_file(), "data spec v1 exists")
    text = SPEC.read_text(encoding="utf-8")
    for phrase in [
        "主键语言无关",
        "documents 规范",
        "chunks 规范",
        "canonical_entities 规范",
        "aliases 规范",
        "provenance 规范",
        "canonical_claims 规范",
        "version_tags 规范",
        "contradiction_seeds 规范",
        "export_bundle 规范",
        "merged 主入口规范",
        "embedding 规范",
        "检索规范",
        "版本 v1 的冻结结论",
    ]:
        expect(phrase in text, f"spec contains '{phrase}'")
    print("PASS: data spec v1 verification completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
