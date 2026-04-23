# PostgreSQL-only 问答系统工程化手册

> 更新时间：2026-04-23  
> 目标：把当前 Diablo II 数据问答系统固化成一套 **可复用、可扩展、可校验** 的 PostgreSQL-only 检索与回答工程方案。

---

## 1. 适用范围

本手册服务于以下目标：

1. **唯一外部数据库是 PostgreSQL**
2. 支持 **alias / pg_trgm + BM25 + vector + graph expansion** 多路召回
3. 支持 **query understanding / prompt rewrite / subquestion planning**
4. 支持 **结构化数值题防幻觉**
5. 支持 **回答阶段引用校验 / release gate**
6. 支持后续 **站点更新 -> chunk schema -> PG bundle -> PG reload** 的持续化流程

这套方法不只适用于 Diablo II，也适用于企业知识库、SOP、漏洞依赖、配置规则、FAQ、运维手册等混合知识场景。

---

## 2. 当前系统的全链路

当前链路已经落成以下主干：

```text
站点抓取 / 原始资料
  -> normalized documents / chunks / canonical entities / claims / provenance
  -> structured support / dict bundle / embedding bundle / strategy bundle
  -> PostgreSQL 导入
  -> Query Understanding
  -> 多路召回 (alias + lexical + bm25 + vector + graph + structured support)
  -> ranking reasons / reason summary / numeric reasoning summary
  -> LLM answer generation
  -> LLM verifier release gate
  -> 最终答案
```

当前仓库对应实现：

- Query Understanding：`app/query_understanding.py`
- PostgreSQL 召回：`app/postgres_store.py`
- QA 聚合：`app/service.py`
- API：`app/main.py`
- CLI：`scripts/d2_pg_cli.py`
- 总体验证：`scripts/verify_full_pg_qa_stack.py`

---

## 3. 全链路安全与稳定设计

### 3.1 输入阶段

目标：提高召回率，同时避免 rewrite 误伤。

当前做法：

1. **黑话 / 缩写 / 错拼先走 alias_dictionary**
2. 再走 `pg_trgm` / term map / canonical hint
3. 根据 query type 注入约束词：
   - numeric -> `breakpoint table`, `rule lookup`, `exact numeric evidence`
   - multi-hop -> `build core gear`, `base item`, `farm area`
4. 同时保留 identity rewrite，避免过度重写导致偏题

### 3.2 召回阶段

当前召回不是单 lane，而是多路并行：

- **alias / trigram lane**：解决黑话、社区简称、错拼
- **lexical lane**：解决 title/text 的精确约束命中
- **BM25 lane**：解决段落级排序
- **vector lane**：解决机制解释、build 推荐、语义问题
- **graph expansion lane**：解决 build -> runeword -> base -> area 的多跳路径
- **structured support lane**：解决 breakpoint / resist / runeword roll 等高风险数值题

融合方式：

- 当前实现用 **weighted RRF**
- 并叠加 source bonus / authority bonus / curated anchor bonus

### 3.3 回答阶段

当前回答器必须遵守：

1. 只能使用 evidence 中给出的事实
2. 关键判断句末必须挂 `[Sx]`
3. 数值题必须引用表项或规则
4. 不能线性插值
5. 证据不足时明确写“证据不足”

### 3.4 Release Gate 阶段

当前新增的 verifier gate 检查：

1. `grounding_gate_passed`
2. `citation_gate_passed`
3. `numeric_gate_passed`
4. `release_ready`

若未通过：

- 自动进入一次 repair 流程
- 修复后再次校验
- 最终把 `answer_verification` / `answer_release_ready` 回写到返回 payload

这对应了 schema 中预留的：

- `qa.answer_drafts`
- `qa.answer_citations`
- `qa.citation_verification_runs`
- `qa.citation_verification_items`
- `qa.final_answer_audits`

---

## 4. 数据字典与 schema 治理建议

### 4.1 必须长期维护的字典

1. `dict.term_dictionary`
2. `dict.alias_dictionary`
3. `dict.item_dictionary`
4. `dict.build_dictionary`
5. `dict.area_dictionary`
6. `dict.monster_dictionary`
7. `dict.rule_dictionary`
8. `dict.query_pattern_dictionary`
9. `qu.retrieval_policies`
10. `qu.answer_constraints`

### 4.2 字典治理原则

1. **canonical name 唯一**
2. alias 与 canonical 分离，不要把 alias 直接当主键
3. 高风险规则进入 `rule_dictionary`，不要只藏在 chunk 文本里
4. Query rewrite 的启发式要表驱动，不要全写死在 prompt 里
5. 数据字典的每次扩展都要能重建 bundle

### 4.3 对其他领域复用时的替换面

把 Diablo II 名词替换成目标领域实体即可：

- item -> 产品 / 文档 / 组件
- monster -> 服务 / 系统 / 风险对象
- runeword -> 方案组合 / 模板 / 配置配方
- breakpoint rule -> 阶梯规则 / SLA / 风险阈值 / 合规门槛

---

## 5. 数据更新与增量流程

推荐流程：

```text
新站点 / 新页面
  -> fetch-tier0
  -> normalize-tier0
  -> merge-production
  -> structured-support
  -> pg-bundle
  -> pg-dict-bundle
  -> pg-embedding-bundle
  -> pg-strategy-bundle
  -> load-pg / load-dict / load-embeddings / load-strategy
  -> full-stack-verify
```

对应 CLI：

```bash
.venv/bin/python scripts/d2_pg_cli.py stage deploy-pg17
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
.venv/bin/python scripts/d2_pg_cli.py load-all --database-url "$DATABASE_URL" --with-vector
.venv/bin/python scripts/d2_pg_cli.py stage smoke-verify
```

如果只是数据已更新、想重建检索资产：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-live-pg
```

如果希望一键从站点刷新到可问答运行态：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-live-pg
```

补充说明：

- 当前阶段默认先做 **smoke 级校验**
- `full-stack-verify` 保留给后续较重的联调/验收
- 开发推进顺序见 `docs/tier0/pgsql开发落地流程.md`

---

## 6. 格式化与 chunk schema 规范

为保证召回质量，推荐明确区分：

### 6.1 Document 层

保存：

- 原始标题
- 来源 URL
- authority tier
- patch/version
- source_id
- metadata

### 6.2 Chunk 层

必须保存：

- `chunk_id`
- `doc_id`
- `chunk_index`
- `text_content`
- `title`
- `source_id`
- `source_url`
- `authority_tier`
- `metadata`
- `embedding`

### 6.3 Structured Support 层

不要和普通 chunk 混存：

- breakpoints
- resistances
- runeword modifiers
- cube recipes
- strategy edges

这些必须能单独召回、单独解释、单独参与 numeric guard。

---

## 7. LLM 配置与运行建议

当前 `.env.local` 已采用：

```conf
LLM_BASE_URL=https://vibediary.app/api/v1
LLM_MODEL=gpt-5.4
LLM_TIMEOUT_SECONDS=90
LLM_MAX_RETRIES=2
LLM_VERIFIER_ENABLED=true
LLM_VERIFIER_MODEL=gpt-5.4
LLM_ANSWER_REPAIR_ATTEMPTS=1
```

工程建议：

1. generation 与 verifier 可先共用同一模型
2. 后续若要降本，可把 verifier 换成更便宜模型
3. 生产环境里 secret 不要写入仓库，建议改用环境注入
4. 必须保留 timeout / retry / repair / release gate

---

## 8. 运维校验矩阵

### 8.1 基础校验

```bash
bash deploy/pgsql17-ubuntu24/verify-running.sh
```

### 8.2 Python 侧链路校验

注意：当前 `scripts/verify_*.py` 已经收敛成**开发验证 / 单元测试风格包装器**，主要用于本地回归与工程验收，不按生产压测脚本设计。

```bash
.venv/bin/python scripts/verify_query_execution_chain.py
.venv/bin/python scripts/verify_postgres_runtime_ready.py
.venv/bin/python scripts/verify_api_pg_runtime.py
.venv/bin/python scripts/verify_llm_reasoned_answers.py
```

### 8.3 一键总校验

```bash
.venv/bin/python scripts/verify_full_pg_qa_stack.py
```

如果你要跑更慢、更重的 LLM 扩展案例：

```bash
RUN_SLOW_LLM_TESTS=true .venv/bin/python scripts/verify_llm_reasoned_answers.py
```

默认只跑稳定的 smoke case，避免把开发期脚本做成生产级长耗时测试。

### 8.4 当前效果快照

如果你想直接看“当前版本效果大概怎么样”，可执行：

```bash
.venv/bin/python scripts/evaluate_current_pg_effect.py
```

或：

```bash
.venv/bin/python scripts/d2_pg_cli.py stage effect-eval
```

它会生成：

- `docs/tier0/verification/current-pg-effect-eval.json`
- `docs/tier0/verification/current-pg-effect-eval.md`

该评估默认覆盖：

- alias/黑话事实题
- 数值题
- 多跳策略题
- 少量 LLM 最终回答题

---

## 9. 预研路径与引用过程

本轮方案采用“先能力映射，再最小可运行落地”的预研路径：

1. 先确认 **PG17 + pgvector + pg_textsearch + pg_trgm + ltree** 是否能覆盖目标能力
2. 再决定 **不强依赖 AGE / Cypher**
3. 再把 schema 拆成：
   - core / d2
   - dict / qu / qa
4. 再把 bundle、CLI、runtime、verifier 串起来
5. 最后以真实问题校验：
   - 黑话事实题
   - 数值断点题
   - 多跳策略题

本轮主要参考来源已记录在：

- `docs/tier0/pgsql17部署与扩展基线方案.md`

建议把外部参考长期限制在：

1. PostgreSQL 官方文档
2. `pgvector` 官方 README
3. `pg_textsearch` 官方 README
4. 本仓库自己的验证脚本与实测记录

---

## 10. 一句话复用模板

如果你后面要把这套路迁移到其他领域，可以直接沿用下面这个模板：

> PostgreSQL-only + dict/qu/qa schema + multi-lane retrieval + structured numeric guard + LLM verifier release gate + bundle/CLI/update workflow

这就是当前仓库最值得长期复用的工程骨架。
