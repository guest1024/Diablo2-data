# Verification Suite

- Generated at: `2026-04-23T10:00:18.629268+00:00`
- Passed: `15/15`

| Check | Status |
|---|---|
| verify_chroma_package | PASS |
| build_snapshot_manifest | PASS |
| verify_snapshot_manifest | PASS |
| build_graph_support_assets | PASS |
| verify_graph_support_assets | PASS |
| verify_bilingual_term_map | PASS |
| verify_curated_anchor_routing | PASS |
| verify_routing_matrix | PASS |
| verify_curated_surface_alignment | PASS |
| build_surface_coverage_report | PASS |
| build_verification_index | PASS |
| build_curated_catalog | PASS |
| build_term_map_catalog | PASS |
| verify_strategy_docs | PASS |
| verify_doc_handbooks | PASS |

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

### build_snapshot_manifest

- status: `PASS`
- stdout tail:
```text
{"total_snapshots": 30, "sources": 5}
```

### verify_snapshot_manifest

- status: `PASS`
- stdout tail:
```text
PASS: snapshot row has required fields: items
PASS: snapshot local path exists: docs/tier0/raw/arreat-summit/items.html
PASS: snapshot row has required fields: monsters
PASS: snapshot local path exists: docs/tier0/raw/arreat-summit/monsters.html
PASS: snapshot row has required fields: quests
PASS: snapshot local path exists: docs/tier0/raw/arreat-summit/quests.html
PASS: snapshot row has required fields: maps
PASS: snapshot local path exists: docs/tier0/raw/arreat-summit/maps.html
PASS: snapshot row has required fields: sitemap
PASS: snapshot local path exists: docs/tier0/raw/diablo2-io/sitemap.xml
PASS: snapshot row has required fields: uniques
PASS: snapshot local path exists: docs/tier0/raw/diablo2-io/uniques.html
```

### build_graph_support_assets

- status: `PASS`
- stdout tail:
```text
{"aliases": 243, "equivalences": 243, "build_archetypes": 9}
```

### verify_graph_support_assets

- status: `PASS`
- stdout tail:
```text
PASS: alias registry contains CTA
PASS: alias registry contains HOTO
PASS: alias registry contains DClone
PASS: alias registry contains SOJ
PASS: alias registry contains 米山
PASS: alias registry contains 安头
PASS: alias registry contains 锤丁
PASS: build registry contains build::hammerdin
PASS: build registry contains build::blizzard-sorceress
PASS: build registry contains build::javazon
PASS: build registry contains build::lightning-sorceress
PASS: build registry contains build::summon-necromancer
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
PASS: 电法是什么？ top8 contains expected hybrid anchor
PASS: 新星电法是什么？ top8 contains expected hybrid anchor
PASS: 冰法是什么？ top8 contains expected hybrid anchor
PASS: 锤丁是什么？ top8 contains expected hybrid anchor
PASS: 陷阱刺客是什么？ top8 contains expected hybrid anchor
PASS: 召唤死灵是什么？ top8 contains expected hybrid anchor
PASS: 橡树之心是什么？ top8 contains expected hybrid anchor
PASS: 死呼是什么？ top8 contains expected hybrid anchor
PASS: 荣耀之链是什么？ top8 contains expected hybrid anchor
PASS: 狮鹫是什么？ top8 contains expected hybrid anchor
PASS: Spirit routes to supported primary evidence
PASS: Spirit prefers primary or structured evidence
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
PASS: community capability doc contains marker: 赫拉迪姆方块
PASS: community capability doc contains marker: 佣兵系统
PASS: community capability doc contains marker: 任务、地图与隐藏关卡
PASS: community capability doc contains marker: 问题类型路由层
PASS: community capability doc contains marker: source-aware answer policy
PASS: community capability doc contains marker: 失败问答回流
PASS: snapshot handbook exists
PASS: snapshot handbook contains marker: 快照链接
PASS: snapshot handbook contains marker: docs/tier0/raw
PASS: snapshot handbook contains marker: snapshot-manifest
PASS: snapshot handbook contains marker: 增量抓取
PASS: snapshot handbook contains marker: 只抓变化页面
```

### verify_doc_handbooks

- status: `PASS`
- stdout tail:
```text
PASS: docs/RAG开发手册.md contains marker: 当前数据层总览
PASS: docs/RAG开发手册.md contains marker: merged 主知识层
PASS: docs/RAG开发手册.md contains marker: chroma-ready 包
PASS: docs/RAG开发手册.md contains marker: curated anchor 层
PASS: docs/RAG开发手册.md contains marker: 当前已经能解决哪些问题
PASS: docs/RAG开发手册.md contains marker: 当前还不够强的地方
PASS: docs/用户使用手册.md exists
PASS: docs/用户使用手册.md contains marker: 快速启动
PASS: docs/用户使用手册.md contains marker: 可以怎么问
PASS: docs/用户使用手册.md contains marker: 回答结果怎么理解
PASS: docs/用户使用手册.md contains marker: 当前系统擅长什么
PASS: docs/用户使用手册.md contains marker: 当前能力边界
```

