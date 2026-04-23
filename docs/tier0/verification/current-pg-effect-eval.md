# Current PostgreSQL QA Effect Evaluation

- Generated at: `2026-04-23T07:08:00.438123+00:00`
- Retrieval summary: `6/6`
- LLM summary: `2/2`
- Rule: retrieval cases count as pass when expected keywords appear in top-3 chunk title/text; LLM cases count as pass when expected markers appear and release gate passes.

## Retrieval Cases

### [PASS] 劳模掉不掉军帽？
- category: `alias_fact`
- backend: `postgres-hybrid`
- query_type: `fact_lookup`
- top_title: `monster_resistances::Mephisto`
- top_source_id: `structured-support`
- top_retrieval_source: `structured_support`
- matched_keywords: `['mephisto', '劳模']`
- reason_summary: `本题是事实查询题，优先依据结构化事实、锚点卡和高权重文本证据。
- monster_resistances::Mephisto: 结构化证据优先；抗性关系：该问题直接询问劳模/墨菲斯托的抗性数据。
- Mephisto / 劳模（Curated Anchor Card）: BM25 命中强；词面/约束命中；社区锚点卡优先
- unique_items::Ars Dul'Mephistos: 结构化证据优先
- unique_items::Harlequin Crest: 结构化证据优先`

### [PASS] SOJ是什么？
- category: `alias_fact`
- backend: `postgres-hybrid`
- query_type: `fact_lookup`
- top_title: `Stone of Jordan / 乔丹（Curated Anchor Card）`
- top_source_id: `curated-anchor`
- top_retrieval_source: `postgres_bm25`
- matched_keywords: `['stone of jordan', '乔丹']`
- reason_summary: `本题是事实查询题，优先依据结构化事实、锚点卡和高权重文本证据。
- Stone of Jordan / 乔丹（Curated Anchor Card）: BM25 命中强；词面/约束命中；社区锚点卡优先
- unique_items::The Stone of Jordan: 结构化证据优先
- All Diablo 2 Resurrected Cube Recipes
        
                                  
        
         • diablo2.io: BM25 命中强
- All Diablo 2 Resurrected Runewords
        
                                  
        
         • diablo2.io: 词面/约束命中`

### [PASS] 超市是什么？
- category: `alias_fact`
- backend: `postgres-hybrid`
- query_type: `fact_lookup`
- top_title: `Chaos Sanctuary / 超市（Curated Anchor Card）`
- top_source_id: `curated-anchor`
- top_retrieval_source: `postgres_bm25`
- matched_keywords: `['chaos sanctuary', '超市']`
- reason_summary: `本题是事实查询题，优先依据结构化事实、锚点卡和高权重文本证据。
- Chaos Sanctuary / 超市（Curated Anchor Card）: BM25 命中强；向量语义相近；词面/约束命中；社区锚点卡优先
- Diablo / 大菠萝（Curated Anchor Card）: BM25 命中强；社区锚点卡优先
- areas::The Chaos Sanctuary: 结构化证据优先
- The Arreat Summit - Basics: BM25 命中强
- All Diablo 2 Resurrected Monsters
        
                                  
        
         • diablo2.io: BM25 命中强；词面/约束命中`

### [PASS] 我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？
- category: `numeric`
- backend: `postgres-hybrid`
- query_type: `numeric_reasoning`
- top_title: `breakpoints::Sorceress`
- top_source_id: `structured-support`
- top_retrieval_source: `structured_support`
- matched_keywords: `['sorceress', 'breakpoint', 'fcr']`
- reason_summary: `本题是数值判断题，优先依据断点表、规则约束和变量来源。
- breakpoints::Sorceress: 结构化证据优先；断点关系：法师 FCR 档位表是该数值问题的核心依据。
- breakpoints::Sorceress (Lightning / Chain Lightning): 结构化证据优先；断点关系：法师 FCR 档位表是该数值问题的核心依据。
- rules::rules: 结构化证据优先；规则关系：数值问题必须优先受规则表约束，避免幻觉插值。
- runewords::Spirit: 结构化证据优先`

### [PASS] 地狱劳模火抗多少？
- category: `numeric`
- backend: `postgres-hybrid`
- query_type: `fact_lookup`
- top_title: `monster_resistances::Mephisto`
- top_source_id: `structured-support`
- top_retrieval_source: `structured_support`
- matched_keywords: `['mephisto', '75', 'fire']`
- reason_summary: `本题是事实查询题，优先依据结构化事实、锚点卡和高权重文本证据。
- monster_resistances::Mephisto: 结构化证据优先；抗性关系：该问题直接询问劳模/墨菲斯托的抗性数据。
- Mephisto / 劳模（Curated Anchor Card）: BM25 命中强；词面/约束命中；社区锚点卡优先
- unique_items::Ars Dul'Mephistos: 结构化证据优先
- skills::MephistoMissile: 结构化证据优先`

### [PASS] 我想玩锤丁，谜团底材去哪里刷最高效？
- category: `strategy`
- backend: `postgres-hybrid`
- query_type: `multi_hop_strategy`
- top_title: `runewords::Enigma`
- top_source_id: `structured-support`
- top_retrieval_source: `structured_support`
- matched_keywords: `['enigma', 'cow', 'ancient tunnels']`
- reason_summary: `本题是多跳策略题，优先依据构筑、核心装备、底材候选与刷图场景关系。
- runewords::Enigma: 结构化证据优先；核心装备关系：该问题涉及谜团，优先展示符文之语本体。
- areas::The Secret Cow Level: 结构化证据优先；刷图场景关系：牛场常作为高密度刷底材区域。
- areas::Ancient Tunnels: 结构化证据优先；刷图场景关系：古代通道是高价值场景候选之一。
- areas::Pit Level 1: 结构化证据优先；刷图场景关系：地穴是常见高价值刷图路线。
- base_items::Mage Plate: 结构化证据优先；底材关系：Mage Plate 是谜团的低力量需求热门底材。`

## LLM Cases

### [PASS] 我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？
- category: `numeric_answer`
- backend: `postgres-hybrid`
- answer_release_ready: `True`
- matched_markers: `['105', '117', 'Spirit']`
- verifier_summary: `answer 严格基于证据。其关键数值判断均可由断点表与 Spirit 的 FCR 词缀范围直接查表得出：[S4] 给出 Spirit 的 Faster Cast Rate 为 +25% 至 +35%，因此 90 FCR 装备后为 115 至 125；[S1] 普通 Sorceress FCR 下一个高于 90 的断点是 105，所以必定上档；[S2] Lightning/Chain Lightning 下一个高于 90 的断点是 117，所以只有 Spirit 至少 27 FCR 时才上档。answer 还引用了 [S3] 的“必须精确查表、不得插值”规则，且实际推理未使用线性插值。术语“精神盾=Spirit Shield”也有 [S5] 支持。`

### [PASS] 我想玩锤丁，谜团底材去哪里刷最高效？
- category: `strategy_answer`
- backend: `postgres-hybrid`
- answer_release_ready: `True`
- matched_markers: `['Mage Plate', 'Enigma', 'The Secret Cow Level']`
- verifier_summary: `answer 严格受限于已给证据：没有声称“最高效”具体是哪张图，而是明确说明证据不足，只列出被结构化标记为 high_value_base_farm_area 的候选区域，并正确引用了对应怪物密度与区域等级。[S2][S3][S4] 对谜团底材的判断也基于 Enigma 的 3 孔胸甲限制以及 Mage Plate / Dusk Shroud 的结构化字段。[S1][S5][S6] 未发现越证据推断、缺失关键引用或数值插值问题。`

