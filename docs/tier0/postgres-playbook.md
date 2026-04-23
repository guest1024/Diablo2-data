# Diablo II PostgreSQL Playbook

这份文档保留为 PostgreSQL 方向的操作入口。

## 推荐阅读顺序

1. `docs/tier0/pgsql17部署与扩展基线方案.md`
   - 说明为什么当前推荐 PostgreSQL 17
   - 说明需要安装哪些扩展
   - 给出 Docker / 单机安装路径
   - 记录本轮预研路径、引用来源与取舍过程

2. `docs/tier0/pgsql统一检索数据库设计.md`
   - 说明当前适配落地的数据库设计
   - 说明后续数据字典如何入库
   - 说明 `BM25 + embedding + graph expansion` 的统一检索结构

3. `docs/tier0/pgsql问答系统工程化手册.md`
   - 说明问答系统全链路怎么做安全、稳定、可复用
   - 说明 release gate / 引用校验 / 更新流程 / CLI
   - 说明这套方案怎么复用到其他领域

4. `docs/tier0/pgsql开发落地流程.md`
   - 说明当前阶段的开发目标是先跑通流程
   - 说明 smoke 校验与后续效果评估的分层
   - 说明一键从站点跑到 live PG 的 CLI 路径

5. `sql/postgres/001_core_schema.sql`
6. `sql/postgres/003_views.sql`
7. `sql/postgres/queries.sql`
8. `sql/postgres/004_dict_query_quality_schema.sql`
9. `sql/postgres/005_dict_query_quality_views.sql`
10. `sql/postgres/query_understanding_queries.sql`
11. `sql/postgres/006_pg_textsearch_indexes.sql`
12. `docs/tier0/postgres-bundle/`
13. `docs/tier0/postgres-dict-bundle/`
14. `docs/tier0/postgres-embedding-bundle/`

## 当前仓库可直接使用的 PostgreSQL 资产

- Schema / SQL：
  - `sql/postgres/001_core_schema.sql`
  - `sql/postgres/002_optional_vector.sql`
  - `sql/postgres/003_views.sql`
  - `sql/postgres/queries.sql`
- 导入与校验：
  - `scripts/build_postgres_bundle.py`
  - `scripts/load_postgres_bundle.py`
  - `scripts/verify_postgres_bundle.py`
  - `scripts/build_pg_dict_bundle.py`
  - `scripts/load_pg_dict_bundle.py`
  - `scripts/verify_pg_dict_bundle.py`
  - `scripts/build_pg_embedding_bundle.py`
  - `scripts/load_pg_embedding_bundle.py`
  - `scripts/verify_pg_embedding_bundle.py`
  - `scripts/verify_query_execution_chain.py`
- 结构化支撑层：
  - `docs/tier0/structured/*.jsonl`
- 数据包：
  - `docs/tier0/postgres-bundle/`

## 当前边界

- 当前仓库仍以 JSONL / Chroma / local graph 为主要运行态，PostgreSQL 方向属于正在增强中的统一检索方案。
- 当前 PostgreSQL 设计已覆盖：
  - alias / trigram
  - structured facts
  - vector-ready schema
  - recursive query examples
- 下一步重点应放在：
  - BM25 lane 真正接入运行态
  - embedding 异步回填
  - gameplay edges 更细化
  - 数据字典 schema 正式化

## 运行时 Query Understanding / Retrieval 链

当前 App 运行时已接入：

- `app/query_understanding.py`
- `app/postgres_store.py`
- `app/service.py`

运行时输出现在会显式返回：

- `retrieval_trace`
- `structured_support`
- `accepted_rewrite`
- `subquestion_plan`
- `retrieval_plan`

可用以下脚本做快速链路校验：

```bash
.venv/bin/python scripts/verify_query_execution_chain.py
.venv/bin/python scripts/verify_full_pg_qa_stack.py
```

说明：当前 `verify_*.py` 已改造成更偏**单元测试 / 开发验证**的轻量包装，不再按生产压测脚本设计；复杂 LLM case 默认不全开，必要时用 `RUN_SLOW_LLM_TESTS=true` 打开扩展集。

## 统一 CLI

用于后续站点更新、格式化、PG bundle 重建：

- `scripts/d2_pg_cli.py`

常用命令：

```bash
.venv/bin/python scripts/d2_pg_cli.py show-plan
.venv/bin/python scripts/d2_pg_cli.py stage deploy-pg17
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-live-pg
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-live-pg
.venv/bin/python scripts/d2_pg_cli.py load-all --database-url <DATABASE_URL> --with-vector
.venv/bin/python scripts/d2_pg_cli.py stage smoke-verify
.venv/bin/python scripts/d2_pg_cli.py stage full-stack-verify
```

## PostgreSQL 运行时适配

当前运行时已经补入 PostgreSQL 检索适配层：

- `app/postgres_store.py`

运行时策略：

- `RETRIEVAL_BACKEND=auto`：优先 PostgreSQL，失败回退本地
- `RETRIEVAL_BACKEND=postgres`：强制 PostgreSQL，若不可用则标记 `local-fallback` / 抛错路径由调用方决定
- `RETRIEVAL_BACKEND=local`：固定使用本地 Chroma + JSONL graph

相关环境变量：

- `DATABASE_URL`
- `RETRIEVAL_BACKEND`

当前 `/health` 已会返回 runtime backend 与 PostgreSQL 可用性。

## PostgreSQL 向量资产包

当前仓库已新增：

- `docs/tier0/postgres-embedding-bundle/`
- `scripts/build_pg_embedding_bundle.py`
- `scripts/load_pg_embedding_bundle.py`
- `scripts/verify_pg_embedding_bundle.py`

该资产包用于把 merged chunk 文本转为可导入 PostgreSQL `d2.chunks.embedding` 的向量数据。

## PostgreSQL BM25 运行时

当前仓库已补入：

- `sql/postgres/006_pg_textsearch_indexes.sql`
- `app/postgres_store.py` 中的 BM25 运行时检测与查询路径

说明：

- 若数据库安装了 `pg_textsearch` 且已建立 BM25 索引，则 PostgreSQL 运行时会尝试 `postgres_bm25` lane。
- 若扩展或索引不可用，则自动回退到现有 PostgreSQL lexical/trigram 路径。


补充：当前应用端在 PostgreSQL 运行时里会根据实际参与的 lane，把 `actual_backend` 区分为 `postgres-lexical` / `postgres-bm25` / `postgres-vector` / `postgres-hybrid`。


补充：当前 PostgreSQL 主 bundle 已纳入 `curated anchor` 层，最新实测计数为 `documents=511`、`chunks=8708`、`chunks_with_embedding=8708`。`超市`、`乔丹` 等 query 已能在 PG 主路径下把 curated anchor 顶到前列。


最新 fresh evidence（2026-04-23，本机实测）：

- `劳模掉不掉军帽？` -> `postgres-hybrid`，Top1 = `Mephisto / 劳模（Curated Anchor Card）`
- `超市是什么？` -> `postgres-hybrid`，Top1 = `Chaos Sanctuary / 超市（Curated Anchor Card）`
- `乔丹是什么？` -> `postgres-hybrid`，Top1 = `Stone of Jordan / 乔丹（Curated Anchor Card）`
- `我的法师现在 FCR 是 90，带上精神盾能上一个档位吗？` -> `postgres-hybrid`，Top1 = `Spirit Shield / 精神盾（Curated Anchor Card）`

说明当前 PostgreSQL 主路径的加权融合，已经能把 curated anchor 在关键 query type 下稳定推到前列。


补充：当前仓库已新增 `sql/postgres/007_strategy_views.sql`，用于把 build -> runeword -> base -> farm area 这类启发式 support 固化成 PostgreSQL 可查询的 strategy edges。


补充：当前仓库已新增 `docs/tier0/postgres-strategy-bundle/` 与 `scripts/build_pg_strategy_bundle.py`，用于把 `d2.strategy_edges` 导出成可版本化、可导入、可校验的正式资产。


补充：当前 `strategy bundle` 不再只是导出文件，已对应到 PostgreSQL 持久表 `d2.strategy_edge_facts`，运行时 graph expansion 会优先消费它。


补充：当前应用返回已新增 `ranking_reasons`，用于解释为什么某个 chunk/结构化证据排在前面，包括 lane 原因与 strategy reason。


补充：当前应用返回已新增 `reason_summary`，用于把 `ranking_reasons` 压缩成可直接供回答阶段消费的解释摘要。


补充：当前仓库已新增 `scripts/verify_api_pg_runtime.py`，用于在 HTTP 层验证 `/health`、`/qa`、`ranking_reasons`、`reason_summary` 与 PostgreSQL-backed runtime。


补充：当前仓库已新增 `scripts/verify_llm_reasoned_answers.py`，用于验证 `use_llm=true` 时最终回答能够消费 `reason_summary` 与 `ranking_reasons`。


补充：当前仓库已新增 `docs/tier0/pgsql问答系统工程化手册.md`，用于把 Query Understanding、多路召回、数值防幻觉、引用校验、更新流程和可复用套路固化成工程手册。
