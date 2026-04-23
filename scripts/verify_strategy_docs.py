#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")
    print(f"PASS: {message}")


def main() -> int:
    path = ROOT / "docs/中英实体映射与知识图谱建设手册.md"
    expect(path.is_file(), "strategy handbook exists")
    text = path.read_text(encoding="utf-8")

    required_markers = [
        "怎么快速做好中文 / 英文实体映射",
        "Alias Lexicon",
        "Community Slang",
        "Abbreviation / Acronym",
        "Alias Graph",
        "Entity Graph",
        "Evidence / Provenance Graph",
        "检索友好型知识图谱",
        "alias-registry.jsonl",
        "term-equivalence.jsonl",
        "build-archetypes.jsonl",
    ]
    for marker in required_markers:
        expect(marker in text, f"strategy handbook contains marker: {marker}")

    source_assessment = ROOT / "docs/tier0/blizzhackers-d2data-source-assessment.md"
    expect(source_assessment.is_file(), "blizzhackers assessment exists")
    source_text = source_assessment.read_text(encoding="utf-8")
    for marker in [
        "blizzhackers/d2data",
        "当前都有了吗",
        "结构化事实源",
        "community strategy",
        "source-aware rerank",
    ]:
        expect(marker in source_text, f"blizzhackers assessment contains marker: {marker}")

    capability_doc = ROOT / "docs/社区问答能力缺口与补强方案.md"
    expect(capability_doc.is_file(), "community capability gap doc exists")
    capability_text = capability_doc.read_text(encoding="utf-8")
    for marker in [
        "物品与装备系统",
        "游戏核心机制",
        "职业与流派",
        "赫拉迪姆方块",
        "佣兵系统",
        "任务、地图与隐藏关卡",
        "问题类型路由层",
        "source-aware answer policy",
        "失败问答回流",
    ]:
        expect(marker in capability_text, f"community capability doc contains marker: {marker}")

    snapshot_doc = ROOT / "docs/快照与增量抓取维护手册.md"
    expect(snapshot_doc.is_file(), "snapshot handbook exists")
    snapshot_text = snapshot_doc.read_text(encoding="utf-8")
    for marker in [
        "快照链接",
        "docs/tier0/raw",
        "snapshot-manifest",
        "增量抓取",
        "只抓变化页面",
    ]:
        expect(marker in snapshot_text, f"snapshot handbook contains marker: {marker}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
