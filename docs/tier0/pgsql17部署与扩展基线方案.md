# PostgreSQL 17 部署与扩展基线方案

> 更新时间：2026-04-23  
> 适用目标：以 **PostgreSQL 17** 作为统一外置检索底座，承载 **BM25 + embedding + 知识图谱/关系扩展** 的多路召回验证与落地。  
> 当前约束：**不强依赖 Apache AGE / Cypher 语法**，只要求 PostgreSQL 具备图扩展与查询优化能力。

---

## 1. 目标与边界

本方案的目标不是“让 PostgreSQL 100% 模拟 Neo4j / Elasticsearch / ChromaDB 的全部产品形态”，而是让 PostgreSQL 具备以下**核心能力组合**：

1. **向量检索**：用 `pgvector` 替代向量数据库的核心能力。
2. **关键词 / BM25 检索**：用 `pg_textsearch` + PostgreSQL 原生 FTS 替代 Elasticsearch 的核心文本排序能力。
3. **模糊别名召回**：用 `pg_trgm` 处理黑话、缩写、错别字、拼写偏差。
4. **知识图谱 / 多跳扩展**：用关系表 + `WITH RECURSIVE` + `ltree` 进行图查询，不要求上游必须用 Cypher。
5. **可观测性与优化**：用 `pg_stat_statements`、索引、物化视图、Explain/Analyze 来做性能治理。

### 不在本方案里强求的内容

- 不把“必须支持 Cypher 语法”作为前置要求。
- 不把“所有机器学习都内嵌在 PG 里完成”作为前置要求。
- 不把“所有业务查询都直接写成 graph query”作为目标；优先考虑**混合检索可落地性**。

---

## 2. 为什么选 PostgreSQL 17 而不是 16 / 18

### 2.1 选择结论

当前推荐基线版本：**PostgreSQL 17**。

原因：

- `pgvector` 官方 README 明确说明支持 **Postgres 13+**，因此 PG17 在向量层是安全选择。  
- `pg_textsearch` 官方 README 明确说明支持 **PostgreSQL 17 和 18**。  
- 在不强依赖 Apache AGE 后，没有必要为了 Cypher 兼容性退回 PG16。  
- 与 PG18 相比，PG17 更适合作为第一版“稳定、可控、易部署”的生产/实验混合基线。

### 2.2 版本对比

| 版本 | 优势 | 问题 | 结论 |
| --- | --- | --- | --- |
| PG16 | 与 AGE 路线更兼容 | 若不走 AGE，优势下降；`pg_textsearch` 主支持不在 16 | 不作为本方案首选 |
| **PG17** | `pgvector` 稳、`pg_textsearch` 支持、部署平衡 | 不是最新主版本 | **推荐基线** |
| PG18 | 新版本、`pg_textsearch` 支持 | 第一版部署与运维风险略高 | 可做后续升级或实验环境 |

---

## 3. 建议安装的扩展清单

### 3.1 必装扩展

#### A. `pgvector`
用途：embedding 存储、相似度检索、HNSW / IVFFlat 索引。

建议用途：
- chunk embedding
- entity embedding
- hybrid recall 的 dense lane

#### B. `pg_textsearch`
用途：BM25 relevance-ranked full-text search。

建议用途：
- chunk 文本主 lexical lane
- title / summary / FAQ / build section 的 BM25 排序
- 与 `pgvector` 做 hybrid fusion

#### C. `pg_trgm`
用途：三元组模糊匹配，适合：
- 黑话
- 缩写
- 错别字
- 拼写偏差
- 社区俗称 / 英中混写

典型场景：
- `劳模 -> Mephisto`
- `军帽 -> Harlequin Crest`
- `SOJ -> Stone of Jordan`
- `锤丁 -> Hammerdin`

#### D. `unaccent`
用途：归一化文本，提高 trigram / lexical 稳定性。

#### E. `ltree`
用途：层级路径建模。

适合：
- 技能树
- 区域/地图层级
- 类目路径
- 预计算图路径缓存

#### F. `pg_stat_statements`
用途：
- 观察慢 SQL
- 分析热点查询
- 做 Explain/Analyze 调优

---

### 3.2 可选扩展

#### A. `pgvectorscale`
用途：大规模向量索引优化、StreamingDiskANN、带标签过滤的 vector search。

建议：
- 第一版先不上
- 当 chunk 数量、embedding 数量、过滤复杂度显著上升时再评估

#### B. `fuzzystrmatch`
用途：额外字符串近似工具。

建议：
- 可装，但不是本方案核心依赖

#### C. `pgai`
用途：AI workflow / vectorizer / semantic search 辅助。

当前结论：
- 可参考，不建议作为主方案硬依赖
- 我在预研时确认其 GitHub 仓库已于 **2026-02-26** 被归档，只适合作为次要参考而非核心链路

---

## 4. 推荐的功能映射

### 4.1 替代 ChromaDB 的核心能力

用：
- `pgvector`
- HNSW / IVFFlat
- 向量表 + 过滤字段 + fusion SQL

### 4.2 替代 Elasticsearch 的核心能力

用：
- `pg_textsearch`：BM25
- `tsvector/tsquery`：原生全文检索
- `pg_trgm`：模糊、别名、黑话、错拼
- `unaccent`：归一化

### 4.3 替代 Neo4j 的“能力”

用：
- `edges` 关系表
- `WITH RECURSIVE`
- `ltree`
- 物化视图 / path cache

> 本方案刻意把“图能力”定义为**关系扩展能力**而不是“必须拥有 Cypher 语法”。

---

## 5. Docker 部署方案（推荐）

### 5.1 为什么推荐 Docker

- 版本更稳定
- 更容易复现
- 更容易切换 PG17 / PG18
- 更适合扩展编译与打包
- 更方便后续 CI 验证

### 5.2 基础镜像

建议使用 PostgreSQL 官方镜像：
- `postgres:17-bookworm`

参考：
- Docker Official Image: https://hub.docker.com/_/postgres

### 5.3 Dockerfile 基线示例

```dockerfile
FROM postgres:17-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    ca-certificates \
    clang \
    make \
    pkg-config \
    postgresql-server-dev-17 \
    postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# pgvector
RUN git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git /tmp/pgvector \
    && make -C /tmp/pgvector \
    && make -C /tmp/pgvector install \
    && rm -rf /tmp/pgvector

# pg_textsearch
RUN git clone https://github.com/timescale/pg_textsearch /tmp/pg_textsearch \
    && make -C /tmp/pg_textsearch \
    && make -C /tmp/pg_textsearch install \
    && rm -rf /tmp/pg_textsearch
```

### 5.4 docker-compose 基线示例

```yaml
services:
  pg:
    build: .
    container_name: d2-pg
    environment:
      POSTGRES_USER: d2
      POSTGRES_PASSWORD: d2pass
      POSTGRES_DB: d2
    ports:
      - "5432:5432"
    volumes:
      - ./pgdata:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d
```

### 5.5 初始化扩展 SQL

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS ltree;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_textsearch;
```

### 5.6 `postgresql.conf` 关键项

`pg_textsearch` 官方 README 明确要求通过 `shared_preload_libraries` 预加载，因此至少需要：

```conf
shared_preload_libraries = 'pg_textsearch,pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

### 5.7 Docker 健康检查建议

```bash
pg_isready -U d2 -d d2
```

---

## 6. Debian / Ubuntu 单机安装方案

### 6.1 安装 PostgreSQL 17

建议优先使用 PostgreSQL 官方 Apt 仓库，而不是仅依赖发行版自带版本。

参考：
- PostgreSQL Debian/Linux downloads: https://www.postgresql.org/download/linux/debian/

官方页面给出的自动配置方式：

```bash
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
```

随后安装 PG17：

```bash
sudo apt update
sudo apt install -y postgresql-17 postgresql-contrib postgresql-server-dev-17
```

### 6.2 安装 `pgvector`

优先尝试包管理：

```bash
sudo apt install -y postgresql-17-pgvector
```

如果仓库没有，再按 `pgvector` 官方 README 用源码安装：

```bash
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 6.3 安装 `pg_textsearch`

按官方 README：

```bash
git clone https://github.com/timescale/pg_textsearch
cd pg_textsearch
make
sudo make install
```

然后在 `postgresql.conf` 里设置：

```conf
shared_preload_libraries = 'pg_textsearch'
```

重启后执行：

```sql
CREATE EXTENSION vector;
CREATE EXTENSION pg_trgm;
CREATE EXTENSION unaccent;
CREATE EXTENSION ltree;
CREATE EXTENSION pg_stat_statements;
CREATE EXTENSION pg_textsearch;
```

---

## 7. 运行后必须验证的能力清单

### 7.1 扩展是否可用

```sql
SELECT extname FROM pg_extension ORDER BY extname;
```

期望至少包括：
- `pg_trgm`
- `vector`
- `pg_textsearch`
- `ltree`
- `unaccent`
- `pg_stat_statements`

### 7.2 向量索引是否可建

```sql
CREATE TABLE test_vectors (id bigserial primary key, embedding vector(3));
CREATE INDEX ON test_vectors USING hnsw (embedding vector_cosine_ops);
```

### 7.3 BM25 索引是否可建

```sql
CREATE TABLE test_docs (id bigserial primary key, content text);
CREATE INDEX test_docs_bm25_idx ON test_docs USING bm25 (content) WITH (text_config='english');
```

### 7.4 trigram 是否可查

```sql
SELECT similarity('laomo', '劳模');
```

> 注意：实际中文场景不要直接依赖这种测试结果；真正的中文黑话检索应走**归一化 alias 表**。

---

## 8. 预研路径与取舍记录

### 8.1 预研目标

目标不是“找一个最像 Neo4j 的 PG 扩展”，而是确定：

1. PostgreSQL 是否能承载 `BM25 + embedding + graph expansion`
2. 哪个版本最适合做统一实验底座
3. 哪些扩展是**稳定、现实、能直接部署**的

### 8.2 实际筛选路径

#### 第一步：明确向量层
调研 `pgvector`：
- 确认支持 Postgres 13+
- 确认支持 HNSW / IVFFlat
- 确认官方 README 直接给出了 hybrid search 示例

结论：**向量层采用 `pgvector`**。

#### 第二步：明确 lexical/BM25 层
调研 PostgreSQL 原生 FTS 与 `pg_textsearch`：
- PostgreSQL 原生 `tsvector` 负责标准全文检索
- `pg_textsearch` 提供 BM25 排序与更现代的 lexical lane
- `pg_textsearch` 官方 README 明确支持 PG17/18，并要求 preload

结论：**关键词/BM25 层采用 `pg_textsearch` + 原生 FTS**。

#### 第三步：明确模糊别名层
调研 `pg_trgm`：
- 官方文档确认提供 similarity / trigram match
- 支持 GIN/GiST
- 适合黑话、缩写、错拼、社区别名

结论：**alias / 黑话召回采用 `pg_trgm`**。

#### 第四步：明确图层
由于你后续明确说明：
- 不要求严格依赖 AGE
- 上游语法不限制
- 重点是能力，不是语法

因此图层改为：
- 关系表
- `WITH RECURSIVE`
- `ltree`
- 物化视图/path cache

结论：**不把 AGE 作为核心前提**。

#### 第五步：评估 AI/ML 扩展
调研 `pgai`：
- 仓库已归档
- 更适合作为参考性工具，而不是主方案硬依赖

结论：**AI workflow 不纳入核心安装基线**。

---

## 9. 中文/中英混合检索的特别说明

这一点非常重要。

`pg_textsearch` 官方 README 说明它和 PostgreSQL text search config 配合工作，典型示例是：
- english
- french
- german
- spanish

但这不等于它天然解决中文分词。

### 推荐做法

对中文 / 中英混合 D2 语料，不要把“中文分词”完全寄希望于数据库内建 parser。

应采用：

1. **离线预分词 / 归一化**
2. 生成额外 lexical 字段，例如：
   - `content_lexical_zh`
   - `content_lexical_mixed`
3. 在 PG 内对这些字段建立：
   - BM25 索引
   - trigram 索引
   - tsvector/simple config

示例：

```text
军帽 哈洛奎因 crest shako unique helm all skills
```

这样：
- 中文黑话
- 英文 canonical
- 社区简称
- 俗称/别名
都能进同一 lexical lane。

---

## 10. 与当前仓库实现的关系

当前仓库已经有一套 PostgreSQL 方向的落地骨架：

- Schema / SQL：
  - `sql/postgres/001_core_schema.sql`
  - `sql/postgres/002_optional_vector.sql`
  - `sql/postgres/003_views.sql`
  - `sql/postgres/queries.sql`
- Bundle / 导入：
  - `scripts/build_postgres_bundle.py`
  - `scripts/load_postgres_bundle.py`
  - `scripts/verify_postgres_bundle.py`
  - `docs/tier0/postgres-bundle/`

但当前这套骨架还属于：
- **PG 能力验证版**
- **结构化与检索融合的第一版**

下一阶段应以本文件为部署基线，把它升级到完整 PG17 检索栈。

---

## 11. 后续演进顺序

推荐顺序：

1. 先把 PG17 环境稳定部署起来
2. 先落：`pg_trgm + pgvector + pg_textsearch + ltree`
3. 先完成：`alias + lexical + vector + graph expansion` 四路召回
4. 再做 rerank / fusion
5. 最后再考虑更重的向量优化扩展（如 `pgvectorscale`）

---

## 12. 引用与参考来源

> 下列来源用于本轮 PG17 方案的版本判断、扩展兼容性确认、安装方式确认与能力边界确认。  
> 本节记录的是“我实际用于判断方案”的来源，而不是泛泛罗列。

### 12.1 PostgreSQL 官方
- PostgreSQL `pg_trgm` 文档：  
  https://www.postgresql.org/docs/current/pgtrgm.html
- PostgreSQL 全文检索介绍：  
  https://www.postgresql.org/docs/current/textsearch-intro.html
- PostgreSQL `ltree` 文档：  
  https://www.postgresql.org/docs/current/ltree.html
- PostgreSQL Debian/Linux 下载与 Apt 仓库说明：  
  https://www.postgresql.org/download/linux/debian/

### 12.2 向量与搜索扩展
- `pgvector` 官方 README：  
  https://github.com/pgvector/pgvector
- `pg_textsearch` 官方 README：  
  https://github.com/timescale/pg_textsearch
- `pgvectorscale` 官方仓库：  
  https://github.com/timescale/pgvectorscale

### 12.3 Docker / 运维
- PostgreSQL Official Docker Image：  
  https://hub.docker.com/_/postgres

### 12.4 AI 辅助扩展参考
- `pgai` 官方仓库（已归档）：  
  https://github.com/timescale/pgai

---

## 13. 一句话结论

如果你的目标是：

> “让 PostgreSQL 作为统一外置检索底座，承载 BM25 + embedding + 知识图谱的多路召回，并具备可查询、可优化、可 Explain 的能力”

那么当前最现实、最稳的选择是：

> **PostgreSQL 17 + pgvector + pg_textsearch + pg_trgm + unaccent + ltree + pg_stat_statements**

而不是把目标继续定义成“必须复刻 Neo4j 语法”。

## 14. 与后续数据更新流程的衔接

本仓库已经补入统一 CLI：

- `scripts/d2_pg_cli.py`

它把“站点抓取 -> normalized docs -> chunk schema -> PostgreSQL bundles -> PostgreSQL 导入”串成了统一入口，便于后续站点更新与增量刷新。

建议后续例行操作：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
```

如果只是站点数据更新后重建 PG 资产，不想重新抓取：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-pg-search
```

## 15. 运行时接入建议

当前代码已补入 PostgreSQL 运行时适配层：

- `app/postgres_store.py`

建议环境变量：

```conf
DATABASE_URL=postgresql://user:pass@host:5432/dbname
RETRIEVAL_BACKEND=auto
```

推荐默认值：

- `RETRIEVAL_BACKEND=auto`
  - PostgreSQL 可用时优先用 PG 做检索
  - 不可用时回退本地 Chroma/JSONL

如果你要强制只走 PG 运行时验证，可设置：

```conf
RETRIEVAL_BACKEND=postgres
```

如果要保留当前本地回归基线，可设置：

```conf
RETRIEVAL_BACKEND=local
```

## 16. PostgreSQL 向量导入补充

在 `pgvector` 已安装、`d2.chunks.embedding` 列已创建的前提下，当前仓库还提供了向量资产包：

- `docs/tier0/postgres-embedding-bundle/`

可直接执行：

```bash
.venv/bin/python scripts/build_pg_embedding_bundle.py
.venv/bin/python scripts/verify_pg_embedding_bundle.py
.venv/bin/python scripts/load_pg_embedding_bundle.py --database-url <DATABASE_URL>
```

## 17. pg_textsearch 运行时接入补充

当前仓库已新增：

- `sql/postgres/006_pg_textsearch_indexes.sql`

用于给 `d2.chunks` 建立 BM25 索引。

当 `pg_textsearch` 已安装、索引已建立时，运行时 `app/postgres_store.py` 会自动尝试：

- `postgres_bm25` lane

否则回退到：

- PostgreSQL lexical/trigram lane

因此当前代码已经兼容“扩展已装”和“扩展暂未装”两种状态。


补充：当前仓库已新增 `sql/postgres/007_strategy_views.sql`，用于把 build -> runeword -> base -> farm area 这类启发式 support 固化成 PostgreSQL 可查询的 strategy edges。

## 18. 当前仓库的实际部署实现

虽然前文给了通用基线，但当前仓库已经落成一套**可直接运行**的 Ubuntu 24.04 + PG17 制品镜像方案：

- 目录：`deploy/pgsql17-ubuntu24/`
- 基底：`ubuntu:24.04`
- apt mirror：`mirrors.tencent.com`
- PostgreSQL：`17.5`（源码编译）
- 扩展：
  - `pgvector`
  - `pg_textsearch`
  - `pg_trgm`
  - `unaccent`
  - `ltree`
  - `hstore`
  - `pg_stat_statements`

关键入口：

```bash
bash deploy/pgsql17-ubuntu24/build-and-up.sh
bash deploy/pgsql17-ubuntu24/verify-running.sh
```

当前部署资产已经包含：

- `Dockerfile`
- `docker-compose.yml`
- `conf/postgresql.conf`
- `init/001_extensions.sql`
- `scripts/entrypoint.sh`
- `scripts/process-init-files.sh`

## 19. 当前实测部署结果

本仓库最新实测结果：

- 容器：`d2-pg17`
- 状态：`healthy`
- 镜像：`pgsql17-ubuntu24_pg17:latest`
- bundle 已加载：
  - 主 bundle
  - dict bundle
  - embedding bundle
  - strategy bundle

最新已验证计数：

- `d2.documents = 511`
- `d2.chunks = 8708`
- `d2.canonical_entities = 661`
- `d2.canonical_claims = 899`
- `d2.provenance = 927`
- `dict.item_dictionary = 1080`
- `dict.term_dictionary = 59`
- `d2.strategy_edge_facts = 57`
- `d2.chunks where embedding is not null = 8708`

## 20. 推荐的部署后验收

部署完成后，建议依次执行：

```bash
bash deploy/pgsql17-ubuntu24/verify-running.sh
.venv/bin/python scripts/verify_postgres_runtime_ready.py
.venv/bin/python scripts/verify_api_pg_runtime.py
.venv/bin/python scripts/verify_llm_reasoned_answers.py
.venv/bin/python scripts/verify_full_pg_qa_stack.py
```

## 21. 预研路径补记

本轮预研不是“先选一个最酷的扩展”，而是按下面顺序做的：

1. 先确认目标能力是 **BM25 + embedding + graph expansion**
2. 再确认并不强依赖 Cypher/AGE
3. 再选 PG17 作为版本基线
4. 再确认扩展组合：
   - `pgvector`
   - `pg_textsearch`
   - `pg_trgm`
   - `unaccent`
   - `ltree`
   - `pg_stat_statements`
5. 再把部署收敛成 Ubuntu 24.04 + Docker + source build + bundle auto load

这个顺序很重要，因为它保证了方案是**从能力需求推到实现**，而不是先被某个扩展绑架。
