#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.service import Diablo2QAService


CASES = [
    {
        "query": "Spirit 是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Spirit",
        "lane": "primary",
    },
    {
        "query": "军帽是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Harlequin Crest",
        "lane": "primary",
    },
    {
        "query": "精神符文之语是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Spirit",
        "lane": "primary",
    },
    {
        "query": "火炬是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Hellfire Torch",
        "lane": "primary",
    },
    {
        "query": "地狱火炬是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Hellfire Torch",
        "lane": "primary",
    },
    {
        "query": "谜团是什么？",
        "expected_source_id": "diablo2-io",
        "expected_retrieval_source": "entity_link",
        "expected_title_contains": "Enigma",
        "lane": "primary",
    },
    {
        "query": "超市是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Chaos Sanctuary",
        "lane": "curated",
    },
    {
        "query": "乔丹是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Stone of Jordan",
        "lane": "curated",
    },
    {
        "query": "无限是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Infinity",
        "lane": "curated",
    },
    {
        "query": "劳模是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Mephisto",
        "lane": "curated",
    },
    {
        "query": "女伯爵是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "The Countess",
        "lane": "curated",
    },
    {
        "query": "古代通道是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Ancient Tunnels",
        "lane": "curated",
    },
    {
        "query": "牛场是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Secret Cow Level",
        "lane": "curated",
    },
    {
        "query": "大菠萝是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Diablo",
        "lane": "curated",
    },
    {
        "query": "眼光是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Insight",
        "lane": "curated",
    },
    {
        "query": "悔恨是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Grief",
        "lane": "curated",
    },
    {
        "query": "刚毅是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Fortitude",
        "lane": "curated",
    },
    {
        "query": "战争召唤是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Call to Arms",
        "lane": "curated",
    },
    {
        "query": "地穴是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "The Pit",
        "lane": "curated",
    },
    {
        "query": "军团圣盾是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Monarch",
        "lane": "curated",
    },
    {
        "query": "精神盾是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Spirit Shield",
        "lane": "curated",
    },
    {
        "query": "虫子是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Andariel Bug",
        "lane": "curated",
    },
    {
        "query": "SOJ是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Stone of Jordan",
        "lane": "curated",
    },
    {
        "query": "CTA是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Call to Arms",
        "lane": "curated",
    },
    {
        "query": "毁灭是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Annihilus",
        "lane": "curated",
    },
    {
        "query": "USC是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Annihilus",
        "lane": "curated",
    },
    {
        "query": "MF是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Magic Find",
        "lane": "curated",
    },
    {
        "query": "刷宝是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Magic Find",
        "lane": "curated",
    },
    {
        "query": "DClone是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Diablo Clone",
        "lane": "curated",
    },
    {
        "query": "暗黑克隆是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Diablo Clone",
        "lane": "curated",
    },
    {
        "query": "巴尔是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Baal",
        "lane": "curated",
    },
    {
        "query": "安达利尔是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Andariel",
        "lane": "curated",
    },
    {
        "query": "HOTO是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Heart of the Oak",
        "lane": "curated",
    },
    {
        "query": "橡树之心是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Heart of the Oak",
        "lane": "curated",
    },
    {
        "query": "BOTD是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Breath of the Dying",
        "lane": "curated",
    },
    {
        "query": "死呼是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Breath of the Dying",
        "lane": "curated",
    },
    {
        "query": "COH是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Chains of Honor",
        "lane": "curated",
    },
    {
        "query": "荣耀之链是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Chains of Honor",
        "lane": "curated",
    },
    {
        "query": "马拉是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Mara's Kaleidoscope",
        "lane": "curated",
    },
    {
        "query": "眼球是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "The Oculus",
        "lane": "curated",
    },
    {
        "query": "格里芬是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Griffon's Eye",
        "lane": "curated",
    },
    {
        "query": "狮鹫是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Griffon's Eye",
        "lane": "curated",
    },
    {
        "query": "法拳是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Magefist",
        "lane": "curated",
    },
    {
        "query": "蛇皮是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Skin of the Vipermagi",
        "lane": "curated",
    },
    {
        "query": "战旅是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "War Traveler",
        "lane": "curated",
    },
    {
        "query": "基德是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Gheed's Fortune",
        "lane": "curated",
    },
    {
        "query": "安头是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Andariel's Visage",
        "lane": "curated",
    },
    {
        "query": "蛛网是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Arachnid Mesh",
        "lane": "curated",
    },
    {
        "query": "年纪是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Crown of Ages",
        "lane": "curated",
    },
    {
        "query": "骨髓是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Marrowwalk",
        "lane": "curated",
    },
    {
        "query": "吉永是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Guillaume's Face",
        "lane": "curated",
    },
    {
        "query": "丧钟是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "The Reaper's Toll",
        "lane": "curated",
    },
    {
        "query": "沙暴是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Sandstorm Trek",
        "lane": "curated",
    },
    {
        "query": "雷神是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Thundergod's Vigor",
        "lane": "curated",
    },
    {
        "query": "尼拉塞克是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Nihlathak",
        "lane": "curated",
    },
    {
        "query": "老P是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Pindleskin",
        "lane": "curated",
    },
    {
        "query": "泰坦是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Titan's Revenge",
        "lane": "curated",
    },
    {
        "query": "鸦霜是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Raven Frost",
        "lane": "curated",
    },
    {
        "query": "塔套是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Tal Rasha's Wrappings",
        "lane": "curated",
    },
    {
        "query": "婚戒是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Bul-Kathos' Wedding Band",
        "lane": "curated",
    },
    {
        "query": "虫链是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Highlord's Wrath",
        "lane": "curated",
    },
    {
        "query": "弓马是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Bowazon",
        "lane": "curated",
    },
    {
        "query": "狼德是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Fury Druid",
        "lane": "curated",
    },
    {
        "query": "陷阱刺客是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Trapsin",
        "lane": "curated",
    },
    {
        "query": "新星电法是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Nova Sorceress",
        "lane": "curated",
    },
    {
        "query": "召唤死灵是什么？",
        "expected_source_id": "curated-anchor",
        "expected_retrieval_source": "lexical",
        "expected_title_contains": "Summon Necromancer",
        "lane": "curated",
    },
]


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

    rows: list[dict[str, object]] = []
    for case in CASES:
        body = service.answer(case["query"], use_llm=False)
        top = body["chunks"][0]
        title = str(top["metadata"]["title"])
        passed = (
            top["metadata"]["source_id"] == case["expected_source_id"]
            and top["retrieval_source"] == case["expected_retrieval_source"]
            and case["expected_title_contains"] in title
        )
        expect(passed, f"{case['query']} routes as expected")
        rows.append(
            {
                "query": case["query"],
                "lane": case["lane"],
                "source_id": top["metadata"]["source_id"],
                "retrieval_source": top["retrieval_source"],
                "title": title,
            }
        )

    out_dir = ROOT / "docs/tier0/verification"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runtime_ingest": ingest,
        "cases": rows,
    }
    (out_dir / "routing-matrix.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Routing Matrix Verification",
        "",
        f"- Generated at: `{report['generated_at']}`",
        f"- Runtime ingest: `{ingest['documents']} documents / {ingest['chunks']} chunks`",
        "",
        "| Query | Lane | Retrieval | Source | Top title |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['query']} | {row['lane']} | {row['retrieval_source']} | {row['source_id']} | {str(row['title']).replace(chr(10), ' ')} |"
        )
    (out_dir / "routing-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)


if __name__ == "__main__":
    raise SystemExit(main())
