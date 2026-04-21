#!/usr/bin/env python3
from __future__ import annotations

import os
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
    ingest = service.ingest()
    base_doc_count = sum(1 for line in (ROOT / "docs/chroma-ready/documents.jsonl").open(encoding="utf-8") if line.strip())
    base_chunk_count = sum(1 for line in (ROOT / "docs/chroma-ready/chunks.jsonl").open(encoding="utf-8") if line.strip())
    curated_doc_count = sum(1 for line in (ROOT / "docs/tier0/curated/documents.jsonl").open(encoding="utf-8") if line.strip())
    curated_chunk_count = sum(1 for line in (ROOT / "docs/tier0/curated/chunks.jsonl").open(encoding="utf-8") if line.strip())
    expect(ingest["documents"] == base_doc_count + curated_doc_count, "runtime ingest includes curated anchor documents")
    expect(ingest["chunks"] == base_chunk_count + curated_chunk_count, "runtime ingest includes curated anchor chunks")

    curated_cases = {
        "超市是什么？": "Chaos Sanctuary / 超市（Curated Anchor Card）",
        "乔丹是什么？": "Stone of Jordan / 乔丹（Curated Anchor Card）",
        "无限是什么？": "Infinity / 无限（Curated Anchor Card）",
        "劳模是什么？": "Mephisto / 劳模（Curated Anchor Card）",
        "女伯爵是什么？": "The Countess / 女伯爵（Curated Anchor Card）",
        "古代通道是什么？": "Ancient Tunnels / 古代通道（Curated Anchor Card）",
        "牛场是什么？": "Secret Cow Level / 牛场（Curated Anchor Card）",
        "大菠萝是什么？": "Diablo / 大菠萝（Curated Anchor Card）",
        "眼光是什么？": "Insight / 眼光（Curated Anchor Card）",
        "悔恨是什么？": "Grief / 悔恨（Curated Anchor Card）",
        "刚毅是什么？": "Fortitude / 刚毅（Curated Anchor Card）",
        "战争召唤是什么？": "Call to Arms / 战争召唤（Curated Anchor Card）",
        "地穴是什么？": "The Pit / 地穴（Curated Anchor Card）",
        "军团圣盾是什么？": "Monarch / 军团圣盾（Curated Anchor Card）",
        "精神盾是什么？": "Spirit Shield / 精神盾（Curated Anchor Card）",
        "虫子是什么？": "Andariel Bug / 虫子（Curated Anchor Card）",
        "SOJ是什么？": "Stone of Jordan / 乔丹（Curated Anchor Card）",
        "CTA是什么？": "Call to Arms / 战争召唤（Curated Anchor Card）",
        "毁灭是什么？": "Annihilus / 毁灭（Curated Anchor Card）",
        "USC是什么？": "Annihilus / 毁灭（Curated Anchor Card）",
        "MF是什么？": "Magic Find / MF / 刷宝（Curated Anchor Card）",
        "刷宝是什么？": "Magic Find / MF / 刷宝（Curated Anchor Card）",
        "DClone是什么？": "Diablo Clone / DClone / 暗黑克隆（Curated Anchor Card）",
        "暗黑克隆是什么？": "Diablo Clone / DClone / 暗黑克隆（Curated Anchor Card）",
        "巴尔是什么？": "Baal / 巴尔（Curated Anchor Card）",
        "安达利尔是什么？": "Andariel / 安达利尔（Curated Anchor Card）",
        "HOTO是什么？": "Heart of the Oak / HOTO（Curated Anchor Card）",
        "BOTD是什么？": "Breath of the Dying / BOTD（Curated Anchor Card）",
        "COH是什么？": "Chains of Honor / COH（Curated Anchor Card）",
        "马拉是什么？": "Mara's Kaleidoscope / 马拉（Curated Anchor Card）",
        "眼球是什么？": "The Oculus / 眼球（Curated Anchor Card）",
        "格里芬是什么？": "Griffon's Eye / 格里芬（Curated Anchor Card）",
        "法拳是什么？": "Magefist / 法拳（Curated Anchor Card）",
        "蛇皮是什么？": "Skin of the Vipermagi / 蛇皮（Curated Anchor Card）",
        "战旅是什么？": "War Traveler / 战旅（Curated Anchor Card）",
        "基德是什么？": "Gheed's Fortune / 基德（Curated Anchor Card）",
        "安头是什么？": "Andariel's Visage / 安头（Curated Anchor Card）",
        "蛛网是什么？": "Arachnid Mesh / 蛛网（Curated Anchor Card）",
        "年纪是什么？": "Crown of Ages / 年纪（Curated Anchor Card）",
        "骨髓是什么？": "Marrowwalk / 骨髓（Curated Anchor Card）",
        "吉永是什么？": "Guillaume's Face / 吉永（Curated Anchor Card）",
        "丧钟是什么？": "The Reaper's Toll / 丧钟（Curated Anchor Card）",
        "沙暴是什么？": "Sandstorm Trek / 沙暴（Curated Anchor Card）",
        "雷神是什么？": "Thundergod's Vigor / 雷神（Curated Anchor Card）",
        "尼拉塞克是什么？": "Nihlathak / 尼拉塞克（Curated Anchor Card）",
        "老P是什么？": "Pindleskin / 老P（Curated Anchor Card）",
        "泰坦是什么？": "Titan's Revenge / 泰坦（Curated Anchor Card）",
        "鸦霜是什么？": "Raven Frost / 鸦霜（Curated Anchor Card）",
        "塔套是什么？": "Tal Rasha's Wrappings / 塔套（Curated Anchor Card）",
        "婚戒是什么？": "Bul-Kathos' Wedding Band / 婚戒（Curated Anchor Card）",
        "虫链是什么？": "Highlord's Wrath / 虫链（Curated Anchor Card）",
        "米山是什么？": "Desert Mercenary / 米山（Curated Anchor Card）",
        "弓马是什么？": "Bowazon / 弓马（Curated Anchor Card）",
        "标马是什么？": "Javazon / 标马（Curated Anchor Card）",
        "狼德是什么？": "Fury Druid / 狼德（Curated Anchor Card）",
        "电法是什么？": "Lightning Sorceress / 电法（Curated Anchor Card）",
        "新星电法是什么？": "Nova Sorceress / 新星电法（Curated Anchor Card）",
        "冰法是什么？": "Blizzard Sorceress / 冰法（Curated Anchor Card）",
        "锤丁是什么？": "Hammerdin / 锤丁（Curated Anchor Card）",
        "陷阱刺客是什么？": "Trapsin / 陷阱刺客（Curated Anchor Card）",
        "召唤死灵是什么？": "Summon Necromancer / 召唤死灵（Curated Anchor Card）",
        "橡树之心是什么？": "Heart of the Oak / HOTO（Curated Anchor Card）",
        "死呼是什么？": "Breath of the Dying / BOTD（Curated Anchor Card）",
        "荣耀之链是什么？": "Chains of Honor / COH（Curated Anchor Card）",
        "狮鹫是什么？": "Griffon's Eye / 格里芬（Curated Anchor Card）",
        "安头是什么？": "Andariel's Visage / 安头（Curated Anchor Card）",
        "蛛网是什么？": "Arachnid Mesh / 蛛网（Curated Anchor Card）",
        "年纪是什么？": "Crown of Ages / 年纪（Curated Anchor Card）",
        "骨髓是什么？": "Marrowwalk / 骨髓（Curated Anchor Card）",
        "吉永是什么？": "Guillaume's Face / 吉永（Curated Anchor Card）",
    }
    for query, expected_title in curated_cases.items():
        body = service.answer(query, use_llm=False)
        top = body["chunks"][0]
        expect(top["metadata"]["source_id"] == "curated-anchor", f"{query} routes to curated anchor source")
        expect(top["metadata"]["title"] == expected_title, f"{query} top title matches curated anchor")

    spirit = service.answer("Spirit 是什么？", use_llm=False)["chunks"][0]
    expect(spirit["metadata"]["source_id"] == "diablo2-io", "Spirit still routes to primary source")
    expect(spirit["retrieval_source"] == "entity_link", "Spirit still prefers entity_link evidence")

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
