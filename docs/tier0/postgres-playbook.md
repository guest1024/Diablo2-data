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

3. `sql/postgres/001_core_schema.sql`
4. `sql/postgres/003_views.sql`
5. `sql/postgres/queries.sql`
6. `sql/postgres/004_dict_query_quality_schema.sql`
7. `sql/postgres/005_dict_query_quality_views.sql`
8. `sql/postgres/query_understanding_queries.sql`
9. `docs/tier0/postgres-bundle/`
10. `docs/tier0/postgres-dict-bundle/`

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
```

## 统一 CLI

用于后续站点更新、格式化、PG bundle 重建：

- `scripts/d2_pg_cli.py`

常用命令：

```bash
.venv/bin/python scripts/d2_pg_cli.py show-plan
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-pg-search
.venv/bin/python scripts/d2_pg_cli.py load-pg --database-url <DATABASE_URL>
.venv/bin/python scripts/d2_pg_cli.py load-dict --database-url <DATABASE_URL>
```
