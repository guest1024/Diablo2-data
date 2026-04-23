# Ubuntu 24.04 + PostgreSQL 17 Docker 部署

这套部署以 **Ubuntu 24.04** 为底板，使用 **mirrors.tencent.com** 作为 apt 源，自动完成：

- PostgreSQL 17 源码编译安装
- `pgvector` 源码编译安装
- `pg_textsearch` 源码编译安装
- 初始化数据库
- 自动创建扩展
- 自动加载仓库内的 schema / bundles

## 目录

- `Dockerfile`
- `docker-compose.yml`
- `build-and-up.sh`
- `init/001_extensions.sql`
- `scripts/entrypoint.sh`
- `conf/postgresql.conf`

## 快速启动

```bash
cd /home/user/diablo2-data
bash deploy/pgsql17-ubuntu24/build-and-up.sh
```

## 仅查看计划（不执行）

```bash
DRY_RUN=true bash deploy/pgsql17-ubuntu24/build-and-up.sh
```

## 启动后连接

```bash
docker exec -it d2-pg17 /opt/postgresql/bin/psql -U d2 -d d2
```

## 检查扩展

```sql
SELECT extname FROM pg_extension ORDER BY extname;
```

## 检查主要表

```sql
SELECT count(*) FROM d2.documents;
SELECT count(*) FROM d2.chunks;
SELECT count(*) FROM d2.canonical_entities;
SELECT count(*) FROM d2.canonical_claims;
SELECT count(*) FROM d2.provenance;
```

## 停止

```bash
docker-compose -f deploy/pgsql17-ubuntu24/docker-compose.yml down
```

## 启动后校验

```bash
bash deploy/pgsql17-ubuntu24/verify-running.sh
```

## 本机验证结果

基于当前工作区，已实际完成以下验证：

- `pgsql17-ubuntu24_pg17:latest` 镜像已构建成功
- `d2-pg17` 容器已启动并 `healthy`
- 扩展已实际加载：`pg_trgm` / `pg_textsearch` / `vector` / `ltree` / `unaccent` / `pg_stat_statements` / `hstore`
- PostgreSQL 主 bundle 已导入
- PostgreSQL 字典 bundle 已导入
- PostgreSQL embedding bundle 已导入
- `d2.documents = 455`
- `d2.chunks = 8652`
- `d2.canonical_entities = 661`
- `d2.canonical_claims = 899`
- `d2.provenance = 927`
- `dict.item_dictionary = 1080`
- `d2.chunks` 中 `embedding IS NOT NULL = 8652`

同时，应用运行时已验证可切到：

- `RETRIEVAL_BACKEND=postgres`
- PostgreSQL-backed query mode（当前 fresh evidence 为 `postgres-lexical`）

如果后续重建镜像，建议仍然执行：

```bash
bash deploy/pgsql17-ubuntu24/build-and-up.sh
bash deploy/pgsql17-ubuntu24/verify-running.sh
```


补充：当前应用端在 PostgreSQL 运行时里会根据实际参与的 lane，把 `actual_backend` 区分为 `postgres-lexical` / `postgres-bm25` / `postgres-vector` / `postgres-hybrid`。


补充：当前 PostgreSQL 主 bundle 已纳入 `curated anchor` 层，最新实测计数为 `documents=511`、`chunks=8708`、`chunks_with_embedding=8708`。`超市`、`乔丹` 等 query 已能在 PG 主路径下把 curated anchor 顶到前列。


补充：当前仓库已新增 `docs/tier0/postgres-strategy-bundle/` 与 `scripts/build_pg_strategy_bundle.py`，用于把 `d2.strategy_edges` 导出成可版本化、可导入、可校验的正式资产。


补充：当前 `strategy bundle` 不再只是导出文件，已对应到 PostgreSQL 持久表 `d2.strategy_edge_facts`，运行时 graph expansion 会优先消费它。


补充：当前应用返回已新增 `ranking_reasons`，用于解释为什么某个 chunk/结构化证据排在前面，包括 lane 原因与 strategy reason。


补充：当前应用返回已新增 `reason_summary`，用于把 `ranking_reasons` 压缩成可直接供回答阶段消费的解释摘要。


补充：当前仓库已新增 `scripts/verify_api_pg_runtime.py`，用于在 HTTP 层验证 `/health`、`/qa`、`ranking_reasons`、`reason_summary` 与 PostgreSQL-backed runtime。


补充：当前仓库已新增 `scripts/verify_llm_reasoned_answers.py`，用于验证 `use_llm=true` 时最终回答能够消费 `reason_summary` 与 `ranking_reasons`。
