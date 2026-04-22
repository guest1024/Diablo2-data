#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.llm_client import chat_completion, extract_json_object

OUT_DIR = ROOT / "docs/tier0/evals"
DATASET_PATH = OUT_DIR / "llm-generated-query-eval-dataset.json"
DATASET_MD_PATH = OUT_DIR / "llm-generated-query-eval-dataset.md"

CHUNK_DATASETS = {
    "curated": ROOT / "docs/tier0/curated/chunks.jsonl",
    "chroma": ROOT / "docs/chroma-ready/chunks.jsonl",
}

ROUTING_SEEDS = [
    {
        "seed_id": "route_spirit",
        "canonical": "Spirit",
        "query_style": "中文定义问法，允许中英混合",
        "expected_source_id": "diablo2-io",
        "expected_title_contains": "Spirit",
        "expected_grounding_mode": "graph+evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Spirit",
        "required_query_terms_any": ["Spirit", "精神"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["怎么做", "底材", "几孔", "哪里刷", "配装", "练法", "符文之语"],
        "prompt_goal": "让玩家在一句话里确认 Spirit 是什么，不扩展成制作/底材问题。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "chroma",
                "chunk_id": "ef481dcd712d1ba501331e7e::chunk-4",
                "role": "primary",
                "focus_terms": ["Spirit", "Runeword", "shield", "weapon", "Monarch"],
            }
        ],
    },
    {
        "seed_id": "route_shako",
        "canonical": "Harlequin Crest / 军帽 / Shako",
        "query_style": "中文俗称定义问法",
        "expected_source_id": "diablo2-io",
        "expected_title_contains": "Harlequin Crest",
        "expected_grounding_mode": "graph+evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Harlequin",
        "required_query_terms_any": ["军帽", "Shako", "Harlequin Crest"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["哪里刷", "掉落", "配装", "练法", "为什么大家都带"],
        "prompt_goal": "让玩家直接问军帽/Shako 是什么，不扩展成刷取或 build 问题。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "chroma",
                "chunk_id": "f828a9fa0999ad35b05c6c5e::chunk-3",
                "role": "primary",
                "focus_terms": ["Shako", "Harlequin Crest", "+2 To All Skills", "Magic Items"],
            }
        ],
    },
    {
        "seed_id": "route_torch",
        "canonical": "Hellfire Torch / 地狱火炬 / 火炬",
        "query_style": "中文俗称定义问法",
        "expected_source_id": "diablo2-io",
        "expected_title_contains": "Hellfire Torch",
        "expected_grounding_mode": "graph+evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Hellfire Torch",
        "required_query_terms_any": ["火炬", "Hellfire Torch", "地狱火炬"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["怎么拿", "红门", "获取流程", "哪里刷", "哪个"],
        "prompt_goal": "让玩家确认火炬这个物品是什么，不扩展到获取流程。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "chroma",
                "chunk_id": "f9e97a8c5a04c5f9483e33e9::chunk-3",
                "role": "primary",
                "focus_terms": ["Hellfire Torch", "Large Charm", "+3 to Random Character Class Skills", "Pandemonium Event"],
            }
        ],
    },
    {
        "seed_id": "route_soj",
        "canonical": "Stone of Jordan / 乔丹 / SOJ",
        "query_style": "中文简称/缩写定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Stone of Jordan",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Stone of Jordan",
        "required_query_terms_any": ["乔丹", "SOJ", "Stone of Jordan"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["哪里刷", "为啥强", "值钱", "交易价"],
        "prompt_goal": "让玩家问清楚乔丹 / SOJ 是什么戒指，不扩展到刷取或价值判断。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::stone-of-jordan::chunk-1",
                "role": "primary",
                "focus_terms": ["Stone of Jordan", "乔丹", "SOJ", "+1 to All Skills"],
            }
        ],
    },
    {
        "seed_id": "route_infinity",
        "canonical": "Infinity / 无限",
        "query_style": "中文简称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Infinity",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Infinity",
        "required_query_terms_any": ["无限", "Infinity"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["底材", "几孔", "长柄", "米山", "给谁用", "符文之语", "哪个"],
        "prompt_goal": "让玩家确认无限是什么符文之语，不扩展到底材选择。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::infinity::chunk-1",
                "role": "primary",
                "focus_terms": ["Infinity", "Ber Mal Ber Ist", "Polearm", "Conviction Aura"],
            }
        ],
    },
    {
        "seed_id": "route_chaos_sanctuary",
        "canonical": "Chaos Sanctuary / 超市",
        "query_style": "玩家黑话定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Chaos Sanctuary",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Chaos",
        "required_query_terms_any": ["超市", "Chaos Sanctuary"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["怎么走", "路线", "封印", "开图", "是不是"],
        "prompt_goal": "让玩家用黑话确认“超市”指什么区域，不扩展成走图问题。",
        "max_query_chars": 8,
        "fallback_query": "超市是啥？",
        "fallback_generation_note": "为避免 definition 查询过长触发 decomposition，使用更短的 source-grounded 黑话问句。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::chaos-sanctuary::chunk-1",
                "role": "primary",
                "focus_terms": ["Chaos Sanctuary", "超市", "Act IV", "River of Flame", "Diablo"],
            }
        ],
    },
    {
        "seed_id": "route_nova_sorc",
        "canonical": "Nova Sorceress / 新星电法",
        "query_style": "中文流派名称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Nova Sorceress",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Nova Sorceress",
        "required_query_terms_any": ["新星电法", "Nova Sorceress", "Nova"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["配装", "加点", "ES", "练法", "怎么玩", "流派"],
        "prompt_goal": "让玩家确认新星电法这个俗称指什么，不展开到配装细节。",
        "fallback_query": "新星电法是啥？",
        "fallback_generation_note": "LLM 多次偏向 ES / build 细节时，使用 source-grounded 保守兜底问句。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::nova-sorceress::chunk-1",
                "role": "primary",
                "focus_terms": ["Nova Sorceress", "新星电法", "Nova", "Lightning"],
            }
        ],
    },
    {
        "seed_id": "route_countess",
        "canonical": "The Countess / 女伯爵",
        "query_style": "中文俗称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "The Countess",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Countess",
        "required_query_terms_any": ["女伯爵", "Countess", "The Countess"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["哪里刷", "掉符文", "路线", "前期一直刷", "哪个"],
        "prompt_goal": "让玩家确认女伯爵是谁/是什么怪，不扩展成刷符文路线问题。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::countess::chunk-1",
                "role": "primary",
                "focus_terms": ["The Countess", "女伯爵", "Tower Cellar Level 5", "Act I"],
            }
        ],
    },
    {
        "seed_id": "route_hoto",
        "canonical": "Heart of the Oak / HOTO / 橡树之心",
        "query_style": "中文简称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Heart of the Oak",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Heart of the Oak",
        "required_query_terms_any": ["HOTO", "橡树之心", "Heart of the Oak"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["底材", "符文", "法系", "适合谁", "用途", "配装"],
        "prompt_goal": "让玩家确认 HOTO / 橡树之心 是什么，不扩展到用途或底材讨论。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::hoto::chunk-1",
                "role": "primary",
                "focus_terms": ["Heart of the Oak", "HOTO", "橡树之心", "Runeword"],
            }
        ],
    },
    {
        "seed_id": "route_cta",
        "canonical": "Call to Arms / 战争召唤 / CTA",
        "query_style": "中文简称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Call to Arms",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Call to Arms",
        "required_query_terms_any": ["CTA", "战争召唤", "Call to Arms"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["BO", "Battle Orders", "给谁用", "用途", "底材", "几孔"],
        "prompt_goal": "让玩家确认 CTA / 战争召唤 是什么，不扩展到 BO 用途或制作要求。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::call-to-arms::chunk-1",
                "role": "primary",
                "focus_terms": ["Call to Arms", "战争召唤", "CTA", "Battle Orders"],
            }
        ],
    },
    {
        "seed_id": "route_mephisto",
        "canonical": "Mephisto / 劳模",
        "query_style": "玩家黑话定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Mephisto",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Mephisto",
        "required_query_terms_any": ["劳模", "Mephisto"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["哪里刷", "崔凡克", "劳模跑法", "掉落", "位置"],
        "prompt_goal": "让玩家确认“劳模”指的是谁，不扩展到刷取路线。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::mephisto::chunk-1",
                "role": "primary",
                "focus_terms": ["Mephisto", "劳模", "Act 3 Boss", "Durance of Hate Level 3"],
            }
        ],
    },
    {
        "seed_id": "route_cow_level",
        "canonical": "Secret Cow Level / 牛场",
        "query_style": "中文黑话定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Secret Cow Level",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Cow",
        "required_query_terms_any": ["牛场", "Secret Cow Level", "Cow Level"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["刷底材", "刷符文", "奶牛关", "怎么开", "红门"],
        "prompt_goal": "让玩家确认“牛场”是什么区域，不扩展到开门或刷图用途。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::secret-cow-level::chunk-1",
                "role": "primary",
                "focus_terms": ["Secret Cow Level", "牛场", "Cow Level", "Hell Bovine"],
            }
        ],
    },
    {
        "seed_id": "route_ancient_tunnels",
        "canonical": "Ancient Tunnels / 古代通道",
        "query_style": "中文区域名称定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Ancient Tunnels",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Ancient Tunnels",
        "required_query_terms_any": ["古代通道", "Ancient Tunnels"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["怎么走", "Lost City", "入口", "路线", "刷图"],
        "prompt_goal": "让玩家确认古代通道是什么区域，不扩展到路线或刷图细节。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::ancient-tunnels::chunk-1",
                "role": "primary",
                "focus_terms": ["Ancient Tunnels", "古代通道", "Act II", "Lost City"],
            }
        ],
    },
    {
        "seed_id": "route_andariel_bug",
        "canonical": "Andariel Bug / 虫子",
        "query_style": "中文社区黑话定义问法",
        "expected_source_id": "curated-anchor",
        "expected_title_contains": "Andariel Bug",
        "expected_grounding_mode": "curated-evidence",
        "expected_intent": "definition",
        "expected_needs_decomposition": False,
        "expected_entity_query_contains": "Andariel Bug",
        "required_query_terms_any": ["虫子", "BUG虫子", "Andariel Bug"],
        "required_phrase_any": ["是什么", "是啥"],
        "avoid_terms": ["怎么卡", "掉落", "任务", "安达利尔", "刷法"],
        "max_query_chars": 12,
        "fallback_query": "BUG虫子是啥？",
        "fallback_generation_note": "定义类黑话查询需要保持极短，避免因上下文包装变成长句后误触发 decomposition。",
        "prompt_goal": "让玩家确认社区黑话“虫子”在这里指什么，不扩展到具体操作。",
        "case_type": "routing",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::andariel-bug::chunk-1",
                "role": "primary",
                "focus_terms": ["Andariel Bug", "虫子", "BUG虫子", "Quest Bug"],
            }
        ],
    },
]

ANALYSIS_SEEDS = [
    {
        "seed_id": "analysis_spirit_shield_base",
        "canonical": "Spirit Shield / 精神盾",
        "query_style": "底材/制作要求问法",
        "expected_intent": "crafting_base",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Spirit",
        "required_query_terms_any": ["精神盾", "Spirit", "Monarch", "圣骑"],
        "required_phrase_any": ["底材", "几孔"],
        "avoid_terms": ["哪里刷", "掉落", "路线", "练法", "区别", "差别", "还是"],
        "prompt_goal": "问题必须围绕精神盾底材、几孔、Monarch 或圣骑盾差异，体现子问题分解价值。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::spirit-shield::chunk-1",
                "role": "anchor",
                "focus_terms": ["Spirit Shield", "精神盾", "Monarch", "军团圣盾"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "ef481dcd712d1ba501331e7e::chunk-4",
                "role": "support",
                "focus_terms": ["Spirit", "shield version", "4 sockets", "Monarch"],
            },
        ],
    },
    {
        "seed_id": "analysis_shako_farm",
        "canonical": "Harlequin Crest / 军帽 / Shako",
        "query_style": "刷取/掉落问法",
        "expected_intent": "farming",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Harlequin",
        "required_query_terms_any": ["军帽", "Shako", "Harlequin Crest", "Mephisto", "Andariel"],
        "required_phrase_any": ["哪里刷", "掉落", "farm"],
        "avoid_terms": ["配装", "为什么强", "是什么", "还是", "更合适"],
        "prompt_goal": "问题必须显式是刷取/掉落问题，最好结合 Harlequin Crest 的 farm spot 线索。",
        "fallback_query": "Harlequin Crest / 军帽 一般哪里刷，Mephisto 和 Andariel 算常见掉落来源吗？",
        "fallback_generation_note": "避免生成 comparison 句式（如“还是哪个更好”），使用更稳定的 farming 问法。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "chroma",
                "chunk_id": "f828a9fa0999ad35b05c6c5e::chunk-6",
                "role": "support",
                "focus_terms": ["farm", "Harlequin Crest", "Andariel", "Diablo", "Baal", "Mephisto"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "facd31cf-535a-5747-9590-cf8347416a95::chunk-17",
                "role": "support",
                "focus_terms": ["Mephisto", "Durance of Hate Level 3", "Treasure class"],
            },
        ],
    },
    {
        "seed_id": "analysis_chaos_path",
        "canonical": "Chaos Sanctuary / 超市",
        "query_style": "位置/路线问法",
        "expected_intent": "location",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Chaos",
        "required_query_terms_any": ["超市", "Chaos Sanctuary", "River of Flame", "封印"],
        "required_phrase_any": ["怎么走", "路线", "从"],
        "avoid_terms": ["掉落", "配装", "build"],
        "prompt_goal": "问题必须围绕从 River of Flame 进入 Chaos Sanctuary 和内部路线/封印顺序。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::chaos-sanctuary::chunk-1",
                "role": "anchor",
                "focus_terms": ["Chaos Sanctuary", "River of Flame", "five seals", "Diablo"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "fc04c06d-a9d3-5f77-8bf3-d5c2ebfd46f9::chunk-28",
                "role": "support",
                "focus_terms": ["River of Flame", "Chaos Sanctuary", "Entered from", "Leads to"],
            },
        ],
    },
    {
        "seed_id": "analysis_pit_usage",
        "canonical": "The Pit / 地穴",
        "query_style": "用途/适用场景问法",
        "expected_intent": "usage",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Pit",
        "required_query_terms_any": ["地穴", "The Pit", "Tamoe Highland", "Pit Level 1"],
        "required_phrase_any": ["用途", "适合", "有啥用"],
        "avoid_terms": ["哪里刷", "还是", "对比", "vs", "farm", "路线"],
        "prompt_goal": "问题必须围绕地穴的用途/适用 farm 场景，不要写成 comparison 问题。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::the-pit::chunk-1",
                "role": "anchor",
                "focus_terms": ["The Pit", "地穴", "Tamoe Highland", "MF"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "fc04c06d-a9d3-5f77-8bf3-d5c2ebfd46f9::chunk-33",
                "role": "support",
                "focus_terms": ["Pit Level 1", "Area level Hell : 85", "Tamoe Highland", "Pit Level 2"],
            },
        ],
    },
    {
        "seed_id": "analysis_infinity_base",
        "canonical": "Infinity / 无限",
        "query_style": "符文之语底材问法",
        "expected_intent": "crafting_base",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Infinity",
        "required_query_terms_any": ["无限", "Infinity", "Scythe", "底材", "米山"],
        "required_phrase_any": ["底材", "几孔", "Scythe", "Polearm"],
        "avoid_terms": ["哪里刷", "是什么", "掉落", "还是", "区别", "取舍", "新星电法", "Nova Sorceress"],
        "prompt_goal": "问题必须以 Infinity / 无限 底材为主语，可结合 Scythe / 自持线索，但不要让新星电法 build 名称抢主实体。",
        "fallback_query": "Infinity / 无限 底材一般用 Scythe 吗，4 孔 Polearm 可以直接做吗？",
        "fallback_generation_note": "为保持 entity_query 稳定落在 Infinity，而不是被 build 名称抢主实体，使用更聚焦的底材问句。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::infinity::chunk-1",
                "role": "anchor",
                "focus_terms": ["Infinity", "Polearm", "Ber Mal Ber Ist", "Conviction Aura"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "2a4ae7bbfb46636717cb024e::chunk-5",
                "role": "support",
                "focus_terms": ["Scythe", "self-wielding Infinity", "Nova Sorceress"],
            },
        ],
    },
    {
        "seed_id": "analysis_nova_build",
        "canonical": "Nova Sorceress / 新星电法",
        "query_style": "练法/配装问法",
        "expected_intent": "build",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Nova",
        "required_query_terms_any": ["新星电法", "Nova Sorceress", "ES", "Memory", "Scythe"],
        "required_phrase_any": ["练法", "配装", "怎么玩"],
        "avoid_terms": ["还是", "对比", "哪里刷", "是什么", "怎么走"],
        "prompt_goal": "问题必须围绕新星电法练法/配装，结合 ES、Memory 或自持 Infinity Scythe 线索，但不要写成 comparison 问题。",
        "fallback_query": "新星电法配装怎么玩，想走 ES 体系的话会用 Memory 预buff，自持 Infinity Scythe 的练法一般怎么搭？",
        "fallback_generation_note": "避免生成“练法怎么走”这类会误触发 location intent 的措辞，使用更稳定的 build 问法。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::nova-sorceress::chunk-1",
                "role": "anchor",
                "focus_terms": ["Nova Sorceress", "新星电法", "Lightning"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "160fffcdfb86c5b582f67812::chunk-3",
                "role": "support",
                "focus_terms": ["Memory", "+3 Energy Shield", "pre-buff", "staves"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "2a4ae7bbfb46636717cb024e::chunk-5",
                "role": "support",
                "focus_terms": ["Scythe", "Infinity", "Nova Sorceress"],
            },
        ],
    },
    {
        "seed_id": "analysis_hoto_usage",
        "canonical": "Heart of the Oak / HOTO / 橡树之心",
        "query_style": "用途/适用职业问法",
        "expected_intent": "usage",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Heart of the Oak",
        "required_query_terms_any": ["HOTO", "Heart of the Oak", "橡树之心", "caster"],
        "required_phrase_any": ["有啥用", "适合", "用途"],
        "avoid_terms": ["是什么", "底材", "几孔", "哪里刷", "配装"],
        "prompt_goal": "问题必须围绕 HOTO 的用途或适用职业，不要退化成定义或制作要求。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::hoto::chunk-1",
                "role": "anchor",
                "focus_terms": ["Heart of the Oak", "HOTO", "橡树之心", "caster"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "65ef56de-0262-5303-ab66-27fe434c060b::chunk-34",
                "role": "support",
                "focus_terms": ["Heart of the Oak", "HOTO", "Maces Staves", "Runeword"],
            },
        ],
    },
    {
        "seed_id": "analysis_cta_usage",
        "canonical": "Call to Arms / 战争召唤 / CTA",
        "query_style": "用途/辅助技能问法",
        "expected_intent": "usage",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Call to Arms",
        "required_query_terms_any": ["CTA", "战争召唤", "Call to Arms", "Battle Orders", "BO"],
        "required_phrase_any": ["有啥用", "适合", "用途"],
        "avoid_terms": ["是什么", "底材", "几孔", "哪里刷", "配装"],
        "prompt_goal": "问题必须围绕 CTA / Battle Orders 的用途或适用场景，不要退化成定义或制作要求。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::call-to-arms::chunk-1",
                "role": "anchor",
                "focus_terms": ["Call to Arms", "战争召唤", "CTA", "Battle Orders"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "6d9323fba864197e2371a555::chunk-4",
                "role": "support",
                "focus_terms": ["Call To Arms", "Battle Orders", "Battle Command", "Battle Cry"],
            },
        ],
    },
    {
        "seed_id": "analysis_mephisto_farm",
        "canonical": "Mephisto / 劳模",
        "query_style": "刷取/掉落问法",
        "expected_intent": "farming",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Mephisto",
        "required_query_terms_any": ["劳模", "Mephisto", "Durance of Hate Level 3"],
        "required_phrase_any": ["哪里刷", "掉落", "farm"],
        "avoid_terms": ["是什么", "路线", "怎么走", "底材", "配装"],
        "prompt_goal": "问题必须围绕劳模 / Mephisto 的刷取或掉落场景，不要写成定义或路线问题。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::mephisto::chunk-1",
                "role": "anchor",
                "focus_terms": ["Mephisto", "劳模", "Act 3 Boss", "Durance of Hate Level 3"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "facd31cf-535a-5747-9590-cf8347416a95::chunk-17",
                "role": "support",
                "focus_terms": ["Mephisto", "Durance of Hate Level 3", "Treasure class"],
            },
        ],
    },
    {
        "seed_id": "analysis_ancient_tunnels_location",
        "canonical": "Ancient Tunnels / 古代通道",
        "query_style": "位置/入口问法",
        "expected_intent": "location",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Ancient Tunnels",
        "required_query_terms_any": ["古代通道", "Ancient Tunnels", "Lost City"],
        "required_phrase_any": ["怎么走", "哪里", "入口"],
        "avoid_terms": ["是什么", "哪里刷", "掉落", "配装", "build"],
        "prompt_goal": "问题必须围绕 Ancient Tunnels / 古代通道 的位置、入口或 Lost City 路线。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::ancient-tunnels::chunk-1",
                "role": "anchor",
                "focus_terms": ["Ancient Tunnels", "古代通道", "Act II", "Lost City"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "fd37d5f139dd65f220847773::chunk-2",
                "role": "support",
                "focus_terms": ["Lost City", "Ancient Tunnels", "Act II"],
            },
        ],
    },
    {
        "seed_id": "analysis_cow_usage",
        "canonical": "Secret Cow Level / 牛场",
        "query_style": "用途/刷图场景问法",
        "expected_intent": "usage",
        "expected_needs_decomposition": True,
        "expected_entity_query_contains": "Cow",
        "required_query_terms_any": ["牛场", "Secret Cow Level", "Cow Level", "刷底材", "刷符文"],
        "required_phrase_any": ["有啥用", "适合", "用途"],
        "avoid_terms": ["是什么", "怎么开", "红门", "哪里刷", "配装"],
        "prompt_goal": "问题必须围绕牛场的用途或常见刷图场景，不要扩展成开门流程。",
        "case_type": "analysis",
        "references": [
            {
                "dataset": "curated",
                "chunk_id": "curated::secret-cow-level::chunk-1",
                "role": "anchor",
                "focus_terms": ["Secret Cow Level", "牛场", "刷怪", "刷底材", "刷符文"],
            },
            {
                "dataset": "chroma",
                "chunk_id": "f636a18b4525547d5fe7fcaa::chunk-11",
                "role": "support",
                "focus_terms": ["Cow King", "Hell Bovine", "Secret Cow Level"],
            },
        ],
    },
]

SEEDS = ROUTING_SEEDS + ANALYSIS_SEEDS
SEED_BY_ID = {seed["seed_id"]: seed for seed in SEEDS}


@lru_cache(maxsize=None)
def load_chunk_index(dataset: str) -> dict[str, dict[str, object]]:
    path = CHUNK_DATASETS[dataset]
    index: dict[str, dict[str, object]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            index[str(row["id"])] = row
    return index


def compact(text: object) -> str:
    return " ".join(str(text or "").split()).strip()


def trim_excerpt(text: str, *, max_chars: int = 280) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def extract_excerpt(content: str, focus_terms: list[str], *, max_chars: int = 280) -> str:
    text = compact(content)
    if not text:
        return ""
    positions: list[int] = []
    lower = text.lower()
    for term in focus_terms:
        token = compact(term)
        if not token:
            continue
        idx = lower.find(token.lower())
        if idx >= 0:
            positions.append(idx)
    if not positions:
        return trim_excerpt(text, max_chars=max_chars)

    start = max(0, min(positions) - 90)
    end = min(len(text), start + max_chars)
    excerpt = text[start:end]
    if start > 0:
        excerpt = "…" + excerpt
    if end < len(text):
        excerpt = excerpt + "…"
    return excerpt


def build_source_context(ref: dict[str, object]) -> dict[str, object]:
    dataset = str(ref["dataset"])
    chunk_id = str(ref["chunk_id"])
    row = load_chunk_index(dataset).get(chunk_id)
    if row is None:
        raise SystemExit(f"Missing reference chunk: dataset={dataset} chunk_id={chunk_id}")

    metadata = dict(row.get("metadata", {}))
    focus_terms = [str(item).strip() for item in ref.get("focus_terms", []) if str(item).strip()]
    keywords = [compact(item) for item in metadata.get("keywords", []) if compact(item)]
    excerpt = extract_excerpt(str(row.get("content", "")), focus_terms or keywords)
    return {
        "dataset": dataset,
        "chunk_id": chunk_id,
        "role": ref.get("role", "support"),
        "source_id": metadata.get("source_id"),
        "source_url": metadata.get("source"),
        "title": compact(metadata.get("title")),
        "keywords": keywords[:8],
        "focus_terms": focus_terms,
        "reference_excerpt": excerpt,
    }


def build_prompt(seed: dict[str, object], contexts: list[dict[str, object]], retry_feedback: str = "") -> str:
    prompt_payload = {
        "seed_id": seed["seed_id"],
        "case_type": seed["case_type"],
        "canonical": seed["canonical"],
        "query_style": seed["query_style"],
        "target_intent": seed.get("expected_intent"),
        "target_needs_decomposition": seed.get("expected_needs_decomposition"),
        "required_query_terms_any": seed.get("required_query_terms_any", []),
        "required_phrase_any": seed.get("required_phrase_any", []),
        "avoid_terms": seed.get("avoid_terms", []),
        "prompt_goal": seed.get("prompt_goal", ""),
    }
    return (
        "请基于给定的 Diablo II 语料证据，生成 1 条 source-grounded 的评测 query。\n"
        "硬性要求：\n"
        "1. 只能使用提供的证据，不要引入证据里没出现的物品、区域、boss、玩法结论。\n"
        "2. query 必须像真实玩家会问的话，优先中文，可中英混合。\n"
        "3. query 必须包含 required_query_terms_any 中至少一个词。\n"
        "4. 如果提供了 required_phrase_any，则 query 还必须包含其中至少一个短语。\n"
        "5. query 不能包含 avoid_terms 中的表达，也不要把问题写偏成其他 intent。\n"
        "6. routing case：保持单跳、清晰，不要写成多问句；analysis case：允许一条问题里带两个相关 facet，但必须仍然对齐 target_intent。\n"
        "7. 尽量使用玩家俗称 / 黑话，但不能丢失可路由性。\n"
        "8. 只输出 JSON object，格式为 {\"query\":..., \"generation_note\":..., \"grounding_used\": [...]}。\n\n"
        f"Seed:\n{json.dumps(prompt_payload, ensure_ascii=False, indent=2)}\n\n"
        f"Evidence contexts:\n{json.dumps(contexts, ensure_ascii=False, indent=2)}"
        + (f"\n\nRetry feedback: {retry_feedback}" if retry_feedback else "")
    )


def validate_query(seed: dict[str, object], query: str) -> str | None:
    normalized = compact(query)
    if not normalized:
        return "query is empty"
    allowed = [str(item).strip() for item in seed.get("required_query_terms_any", []) if str(item).strip()]
    if allowed and not any(term.lower() in normalized.lower() for term in allowed):
        return f"query missing required grounding term from {allowed}"
    required_phrases = [str(item).strip() for item in seed.get("required_phrase_any", []) if str(item).strip()]
    if required_phrases and not any(term.lower() in normalized.lower() for term in required_phrases):
        return f"query missing required phrase from {required_phrases}"
    for term in seed.get("avoid_terms", []):
        token = str(term).strip()
        if token and token.lower() in normalized.lower():
            return f"query contains avoided term: {token}"
    max_query_chars = seed.get("max_query_chars")
    if max_query_chars is not None and len(normalized) > int(max_query_chars):
        return f"query exceeds max_query_chars={max_query_chars}"
    if seed.get("expected_needs_decomposition") is False and len(normalized) > 34:
        return "routing query too long / likely over-composed"
    return None


def generate_case(seed: dict[str, object]) -> dict[str, object]:
    contexts = [build_source_context(ref) for ref in seed.get("references", [])]
    last_error = "unknown"
    retry_feedback = ""
    for attempt in range(1, 6):
        try:
            content = chat_completion(
                [
                    {
                        "role": "system",
                        "content": (
                            "你是 Diablo II 检索评测集构造器。"
                            "你的任务是严格基于证据生成 query。"
                            "只输出 JSON object，不要输出解释。"
                        ),
                    },
                    {"role": "user", "content": build_prompt(seed, contexts, retry_feedback=retry_feedback)},
                ],
                temperature=0.0,
                max_tokens=700,
            )
        except Exception as exc:
            last_error = f"attempt={attempt} api_error={exc.__class__.__name__}: {exc}"
            retry_feedback = (
                f"上一轮请求失败：{exc.__class__.__name__}。"
                "请在下一次成功响应时继续只输出满足约束的 JSON。"
            )
            continue
        payload = extract_json_object(content) or {}
        query = compact(payload.get("query", ""))
        error = validate_query(seed, query)
        if error:
            last_error = f"attempt={attempt} {error}"
            retry_feedback = f"上一版结果无效：{error}。请严格修正，只输出满足约束的 JSON。"
            continue

        reference_titles = [row["title"] for row in contexts]
        reference_source_ids = sorted({str(row["source_id"]) for row in contexts if row.get("source_id")})
        reference_keywords: list[str] = []
        for row in contexts:
            for keyword in row.get("keywords", []):
                token = compact(keyword)
                if token and token not in reference_keywords:
                    reference_keywords.append(token)

        return {
            "id": seed["seed_id"],
            "seed_id": seed["seed_id"],
            "query": query,
            "case_type": seed["case_type"],
            "canonical": seed["canonical"],
            "query_style": seed["query_style"],
            "generation_note": compact(payload.get("generation_note", "")),
            "grounding_used": [compact(item) for item in payload.get("grounding_used", []) if compact(item)],
            "expected_intent": seed.get("expected_intent"),
            "expected_needs_decomposition": seed.get("expected_needs_decomposition"),
            "expected_entity_query_contains": seed.get("expected_entity_query_contains"),
            "expected_source_id": seed.get("expected_source_id"),
            "expected_title_contains": seed.get("expected_title_contains"),
            "expected_grounding_mode": seed.get("expected_grounding_mode"),
            "reference_source_ids": reference_source_ids,
            "reference_titles": reference_titles,
            "reference_keywords": reference_keywords[:12],
            "source_contexts": contexts,
        }

    fallback_query = compact(seed.get("fallback_query", ""))
    if fallback_query:
        return {
            "id": seed["seed_id"],
            "seed_id": seed["seed_id"],
            "query": fallback_query,
            "case_type": seed["case_type"],
            "canonical": seed["canonical"],
            "query_style": seed["query_style"],
            "generation_note": compact(seed.get("fallback_generation_note", "LLM generation fallback")),
            "grounding_used": [row["title"] for row in contexts],
            "expected_intent": seed.get("expected_intent"),
            "expected_needs_decomposition": seed.get("expected_needs_decomposition"),
            "expected_entity_query_contains": seed.get("expected_entity_query_contains"),
            "expected_source_id": seed.get("expected_source_id"),
            "expected_title_contains": seed.get("expected_title_contains"),
            "expected_grounding_mode": seed.get("expected_grounding_mode"),
            "reference_source_ids": sorted({str(row["source_id"]) for row in contexts if row.get("source_id")}),
            "reference_titles": [row["title"] for row in contexts],
            "reference_keywords": [keyword for row in contexts for keyword in row.get("keywords", [])][:12],
            "source_contexts": contexts,
        }

    raise SystemExit(f"LLM dataset generation failed for {seed['seed_id']}: {last_error}")


def generate_cases() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    seen_queries: set[str] = set()
    for seed in SEEDS:
        row = generate_case(seed)
        key = row["query"].lower()
        if key in seen_queries:
            raise SystemExit(f"Duplicate generated query detected: {row['query']}")
        seen_queries.add(key)
        cases.append(row)
    return cases


def write_outputs(cases: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator_model": "llm_via_current_config",
        "generator_mode": "source_grounded_per_seed",
        "case_count": len(cases),
        "cases": cases,
    }
    DATASET_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# 基于 Diablo2 语料生成的 Query Eval Dataset",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- case_count: `{payload['case_count']}`",
        "- generator_mode: `source_grounded_per_seed`",
        "- note: 每条 query 都由当前配置的大模型生成，但生成时显式提供了仓库内 Diablo2 语料证据，不再使用脱离语料的通用 seed prompting。",
        "",
        "## Cases",
        "",
    ]
    for row in cases:
        lines.extend(
            [
                f"### {row['seed_id']}",
                f"- query: `{row['query']}`",
                f"- case_type: `{row['case_type']}`",
                f"- canonical: `{row['canonical']}`",
                f"- expected_intent: `{row.get('expected_intent')}`",
                f"- expected_source_id: `{row.get('expected_source_id')}`",
                f"- expected_title_contains: `{row.get('expected_title_contains')}`",
                f"- generation_note: `{row.get('generation_note')}`",
                f"- reference_titles: `{json.dumps(row.get('reference_titles', []), ensure_ascii=False)}`",
                f"- reference_keywords: `{json.dumps(row.get('reference_keywords', []), ensure_ascii=False)}`",
                "- source_contexts:",
            ]
        )
        for ctx in row.get("source_contexts", []):
            lines.extend(
                [
                    f"  - role: `{ctx['role']}` | source_id: `{ctx['source_id']}` | title: `{ctx['title']}`",
                    f"  - excerpt: `{ctx['reference_excerpt']}`",
                ]
            )
        lines.append("")
    DATASET_MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    cases = generate_cases()
    write_outputs(cases)
    print(json.dumps({"case_count": len(cases), "path": str(DATASET_PATH.relative_to(ROOT))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
