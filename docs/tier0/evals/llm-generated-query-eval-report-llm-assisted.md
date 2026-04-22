# LLM Generated Query Eval Report

- generated_at: `2026-04-22T13:03:12.310593+00:00`
- dataset_path: `docs/tier0/evals/llm-generated-query-eval-dataset.json`
- use_llm: `True`
- passed: `25/25`

## By type

- routing: `14/14`
- analysis: `11/11`

## By expected intent

- definition: `14/14`
- crafting_base: `2/2`
- farming: `2/2`
- location: `2/2`
- usage: `4/4`
- build: `1/1`

## By actual grounding mode

- graph+evidence: `4/4`
- curated-evidence: `21/21`

## Metrics

- entity_query: `25/25`
- grounding_mode: `14/14`
- intent: `25/25`
- needs_decomposition: `25/25`
- top_source_id: `14/14`
- top_title: `14/14`

## Failures

- none

## Cases by expected intent

### definition
- [PASS] `route_spirit` | query=`暗黑2里的 Spirit 是什么？` | actual_intent=`definition` | entity_query=`暗黑2里的 Spirit 是什么？`
- [PASS] `route_shako` | query=`军帽是啥？` | actual_intent=`definition` | entity_query=`Harlequin Crest`
- [PASS] `route_torch` | query=`暗黑2里火炬是啥？` | actual_intent=`definition` | entity_query=`Hellfire Torch`
- [PASS] `route_soj` | query=`乔丹是啥戒指？` | actual_intent=`definition` | entity_query=`The Stone of Jordan Unique Ring`
- [PASS] `route_infinity` | query=`暗黑2里无限是啥？` | actual_intent=`definition` | entity_query=`Infinity`
- [PASS] `route_chaos_sanctuary` | query=`超市是啥` | actual_intent=`definition` | entity_query=`Chaos Sanctuary`
- [PASS] `route_nova_sorc` | query=`新星电法是什么？` | actual_intent=`definition` | entity_query=`Nova Sorceress`
- [PASS] `route_countess` | query=`暗黑2里女伯爵是什么怪？` | actual_intent=`definition` | entity_query=`The Countess`
- [PASS] `route_hoto` | query=`HOTO 是什么？` | actual_intent=`definition` | entity_query=`Heart of the Oak`
- [PASS] `route_cta` | query=`CTA 是什么？` | actual_intent=`definition` | entity_query=`Call to Arms`
- [PASS] `route_mephisto` | query=`劳模是啥？` | actual_intent=`definition` | entity_query=`Mephisto`
- [PASS] `route_cow_level` | query=`牛场是啥？` | actual_intent=`definition` | entity_query=`Secret Cow Level`
- [PASS] `route_ancient_tunnels` | query=`古代通道是什么？` | actual_intent=`definition` | entity_query=`Ancient Tunnels`
- [PASS] `route_andariel_bug` | query=`暗黑2里说的虫子是啥？` | actual_intent=`definition` | entity_query=`Andariel Bug`

### crafting_base
- [PASS] `analysis_spirit_shield_base` | query=`精神盾底材一般是不是 Monarach，做 Spirit 盾要几孔？` | actual_intent=`crafting_base` | entity_query=`Spirit Shield`
- [PASS] `analysis_infinity_base` | query=`无限底材用几孔 Polearm，Scythe 能不能做？` | actual_intent=`crafting_base` | entity_query=`Infinity`

### farming
- [PASS] `analysis_shako_farm` | query=`军帽 Shako 哪里刷？想问 Hell Mephisto 掉落 farm 是否靠谱。` | actual_intent=`farming` | entity_query=`Harlequin Crest`
- [PASS] `analysis_mephisto_farm` | query=`劳模在 Durance of Hate Level 3 farm 的话主要掉落怎么样，Hell 难度的 treasure class 值不值得刷？` | actual_intent=`farming` | entity_query=`Mephisto`

### location
- [PASS] `analysis_chaos_path` | query=`从 River of Flame 进超市怎么走，Chaos Sanctuary 里面五个封印的路线一般怎么跑？` | actual_intent=`location` | entity_query=`Chaos Sanctuary`
- [PASS] `analysis_ancient_tunnels_location` | query=`A2 Lost City 的古代通道入口在哪里，怎么走？` | actual_intent=`location` | entity_query=`Ancient Tunnels`

### usage
- [PASS] `analysis_pit_usage` | query=`地穴（The Pit）有啥用，适合拿来做 MF 和刷 85 场景吗？` | actual_intent=`usage` | entity_query=`The Pit`
- [PASS] `analysis_hoto_usage` | query=`HOTO 有啥用，适合哪些 caster 职业？` | actual_intent=`usage` | entity_query=`Heart of the Oak`
- [PASS] `analysis_cta_usage` | query=`CTA 有啥用，除了 BO 以外适合拿来做辅助吗？` | actual_intent=`usage` | entity_query=`Call to Arms`
- [PASS] `analysis_cow_usage` | query=`牛场有啥用，适合刷底材和刷符文吗？` | actual_intent=`usage` | entity_query=`Secret Cow Level`

### build
- [PASS] `analysis_nova_build` | query=`新星电法配装怎么玩，ES 用 Memory 预buff、自持 Infinity Scythe 这套练法怎么搭？` | actual_intent=`build` | entity_query=`Nova Sorceress`

