# Verification Suite

- Generated at: `2026-04-22T05:38:34.822027+00:00`
- Passed: `14/14`

| Check | Status |
|---|---|
| verify_chroma_package | PASS |
| verify_bilingual_term_map | PASS |
| verify_curated_anchor_routing | PASS |
| verify_grounding_contract | PASS |
| verify_query_analysis_contract | PASS |
| verify_llm_execution_path | PASS |
| verify_llm_eval_dataset_grounding | PASS |
| verify_routing_matrix | PASS |
| verify_curated_surface_alignment | PASS |
| build_surface_coverage_report | PASS |
| build_verification_index | PASS |
| build_curated_catalog | PASS |
| build_term_map_catalog | PASS |
| verify_strategy_docs | PASS |

## Check tails

### verify_chroma_package

- status: `PASS`
- stdout tail:
```text
PASS: chroma chunks exist
PASS: chroma README exists
PASS: chroma document count matches manifest
PASS: chroma chunk count matches manifest
PASS: chroma documents stay aligned with merged normalized documents
PASS: chroma chunks stay aligned with merged chunks
PASS: chroma documents use unified schema
PASS: chroma chunks use unified schema
PASS: chroma chunks include language metadata
PASS: chroma chunks include doc_type metadata
PASS: chroma chunks include game_variant metadata
PASS: chroma package verification completed
```

### verify_bilingual_term_map

- status: `PASS`
- stdout tail:
```text
PASS: aliases are non-empty strings: 安达利尔
PASS: term key is valid: 毁灭
PASS: payload is object: 毁灭
PASS: canonical_hint exists: 毁灭
PASS: aliases exist: 毁灭
PASS: aliases are non-empty strings: 毁灭
PASS: term key is valid: USC
PASS: payload is object: USC
PASS: canonical_hint exists: USC
PASS: aliases exist: USC
PASS: aliases are non-empty strings: USC
PASS: validated 71 bilingual term mappings
```

### verify_curated_anchor_routing

- status: `PASS`
- stdout tail:
```text
PASS: 召唤死灵是什么？ routes to curated anchor source
PASS: 召唤死灵是什么？ top title matches curated anchor
PASS: 橡树之心是什么？ routes to curated anchor source
PASS: 橡树之心是什么？ top title matches curated anchor
PASS: 死呼是什么？ routes to curated anchor source
PASS: 死呼是什么？ top title matches curated anchor
PASS: 荣耀之链是什么？ routes to curated anchor source
PASS: 荣耀之链是什么？ top title matches curated anchor
PASS: 狮鹫是什么？ routes to curated anchor source
PASS: 狮鹫是什么？ top title matches curated anchor
PASS: Spirit still routes to primary source
PASS: Spirit still prefers entity_link evidence
```

### verify_grounding_contract

- status: `PASS`
- stdout tail:
```text
PASS: 无限是什么？ falls back to curated evidence grounding
PASS: 无限是什么？ does not expose noisy graph grounding ids
PASS: 无限是什么？ suppresses unrelated graph claims
PASS: 无限是什么？ suppresses unrelated graph provenance
PASS: 无限是什么？ still returns source URLs
PASS: 无限是什么？ top evidence chunk is the curated anchor
PASS: 橡树之心是什么？ falls back to curated evidence grounding
PASS: 橡树之心是什么？ does not expose noisy graph grounding ids
PASS: 橡树之心是什么？ suppresses unrelated graph claims
PASS: 橡树之心是什么？ suppresses unrelated graph provenance
PASS: 橡树之心是什么？ still returns source URLs
PASS: 橡树之心是什么？ top evidence chunk is the curated anchor
```

### verify_query_analysis_contract

- status: `PASS`
- stdout tail:
```text
PASS: 新星电法是什么 keeps precise matched terms
PASS: 新星电法是什么 deterministic analysis avoids external LLM in contract test
PASS: 新星电法是什么 keeps simple queries undecomposed
PASS: 无限符文之语底材 intent classified as crafting_base
PASS: 无限符文之语底材 has rewritten queries
PASS: 无限符文之语底材 has enough retrieval queries
PASS: 无限符文之语底材 has entity query
PASS: 无限符文之语底材 deterministic analysis avoids external LLM in contract test
PASS: 无限符文之语底材 emits stable subquestions
PASS: QA payload exposes query analysis
PASS: QA payload exposes retrieval plan
PASS: QA evidence chunks keep route contributions
```

### verify_llm_execution_path

- status: `PASS`
- stdout tail:
```text
PASS: LLM execution path returns an answer payload
PASS: LLM execution path preserves query analysis
PASS: LLM answer still cites sources
```

### verify_llm_eval_dataset_grounding

- status: `PASS`
- stdout tail:
```text
PASS: analysis_nova_build source_context[3] dataset is valid
PASS: analysis_nova_build source_context[3] keeps chunk_id
PASS: analysis_nova_build source_context[3] keeps source_id
PASS: analysis_nova_build source_context[3] keeps title
PASS: analysis_nova_build source_context[3] keeps reference_excerpt
PASS: all registered seeds are present in dataset
PASS: llm-generated-query-eval-report-retrieval-only.json exists
PASS: llm-generated-query-eval-report-retrieval-only.json total matches dataset size
PASS: llm-generated-query-eval-report-retrieval-only.json is fully green
PASS: llm-generated-query-eval-report-llm-assisted.json exists
PASS: llm-generated-query-eval-report-llm-assisted.json total matches dataset size
PASS: llm-generated-query-eval-report-llm-assisted.json is fully green
```

### verify_routing_matrix

- status: `PASS`
- stdout tail:
```text
PASS: 尼拉塞克是什么？ routes as expected
PASS: 老P是什么？ routes as expected
PASS: 泰坦是什么？ routes as expected
PASS: 鸦霜是什么？ routes as expected
PASS: 塔套是什么？ routes as expected
PASS: 婚戒是什么？ routes as expected
PASS: 虫链是什么？ routes as expected
PASS: 弓马是什么？ routes as expected
PASS: 狼德是什么？ routes as expected
PASS: 陷阱刺客是什么？ routes as expected
PASS: 新星电法是什么？ routes as expected
PASS: 召唤死灵是什么？ routes as expected
```

### verify_curated_surface_alignment

- status: `PASS`
- stdout tail:
```text
PASS: routing source is curated-anchor for 陷阱刺客是什么？
PASS: routing title exists in curated docs for 陷阱刺客是什么？
PASS: routing source is curated-anchor for 新星电法是什么？
PASS: routing title exists in curated docs for 新星电法是什么？
PASS: routing source is curated-anchor for 召唤死灵是什么？
PASS: routing title exists in curated docs for 召唤死灵是什么？
PASS: term map contains alias SOJ
PASS: term map contains alias CTA
PASS: term map contains alias ULC
PASS: term map contains alias MF
PASS: term map contains alias DClone
PASS: term map contains alias USC
```

### build_surface_coverage_report

- status: `PASS`
- stdout tail:
```text
  "curated_anchor_documents": 56,
  "curated_anchor_chunks": 56,
  "chroma_ready_documents": 455,
  "chroma_ready_chunks": 8652,
  "runtime_documents": 511,
  "runtime_chunks": 8708,
  "routing_matrix_total_queries": 66,
  "routing_lanes": {
    "primary": 6,
    "curated": 60
  }
}
```

### build_verification_index

- status: `PASS`
- stdout tail:
```text
    "curated_routing_cases": 60,
    "term_map_entries": 71,
    "required_aliases": [
      "SOJ",
      "CTA",
      "ULC",
      "MF",
      "DClone",
      "USC"
    ]
  }
}
```

### build_curated_catalog

- status: `PASS`
- stdout tail:
```text
{"curated_cards": 56}
```

### build_term_map_catalog

- status: `PASS`
- stdout tail:
```text
{"entries": 71}
```

### verify_strategy_docs

- status: `PASS`
- stdout tail:
```text
PASS: blizzhackers assessment contains marker: community strategy
PASS: blizzhackers assessment contains marker: source-aware rerank
PASS: community capability gap doc exists
PASS: community capability doc contains marker: 物品与装备系统
PASS: community capability doc contains marker: 游戏核心机制
PASS: community capability doc contains marker: 职业与流派
PASS: community capability doc contains marker: 赫拉迪姆方块
PASS: community capability doc contains marker: 佣兵系统
PASS: community capability doc contains marker: 任务、地图与隐藏关卡
PASS: community capability doc contains marker: 问题类型路由层
PASS: community capability doc contains marker: source-aware answer policy
PASS: community capability doc contains marker: 失败问答回流
```

