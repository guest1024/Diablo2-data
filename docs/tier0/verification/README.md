# Verification Artifacts

本目录用于沉淀第一版系统的验证证据，方便后续继续扩术语、扩锚点、扩检索能力时做回归。

## 当前重点文件

- `verification-suite.md`
  - 当前总验证套件结果
- `verification-index.md`
  - 验证总览入口
- `routing-matrix.md`
  - query -> lane -> source -> title 的路由矩阵
- `surface-coverage-report.md`
  - term map / curated / runtime 覆盖面统计
- `curated-surface-alignment.md`
  - curated docs / chunks / routing / alias 的对齐校验
- `curated-catalog.md`
  - 每张 curated 锚点卡及其对应 query 的总览
- `term-map-catalog.md`
  - bilingual term map 的条目总览
- `../中英实体映射与知识图谱建设手册.md`
  - 中文 / 英文实体映射与知识图谱建设重点说明
- `manual-gap-check-2026-04-21.md`
  - 人工核验与阶段性结论

## 推荐查看顺序

1. `verification-index.md`
2. `verification-suite.md`
3. `routing-matrix.md`
4. `surface-coverage-report.md`
5. `curated-surface-alignment.md`
6. `curated-catalog.md`
7. `term-map-catalog.md`
8. `../中英实体映射与知识图谱建设手册.md`

## 常用重建命令

```bash
source .venv/bin/activate
python scripts/verify_chroma_package.py
python scripts/build_snapshot_manifest.py
python scripts/verify_snapshot_manifest.py
python scripts/build_graph_support_assets.py
python scripts/verify_graph_support_assets.py
python scripts/verify_bilingual_term_map.py
python scripts/verify_curated_anchor_routing.py
python scripts/verify_routing_matrix.py
python scripts/verify_curated_surface_alignment.py
python scripts/build_surface_coverage_report.py
python scripts/build_verification_index.py
python scripts/build_curated_catalog.py
python scripts/build_term_map_catalog.py
python scripts/verify_strategy_docs.py
python scripts/verify_doc_handbooks.py
python scripts/verify_first_system_stack.py
```

## 当前状态摘要

- runtime docs / chunks：`511 / 8708`
- bilingual term map entries：`71`
- curated anchors：`56`
- routing matrix queries：`66`
- verification suite：`15/15 PASS`
