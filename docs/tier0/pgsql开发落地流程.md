# PostgreSQL-only 开发落地流程

> 更新时间：2026-04-23  
> 目标：先把 **抓取 -> 格式化 -> bundle -> PG 导入 -> API 可问答** 整个流程跑通，再做召回效果与问答效果评估。

---

## 1. 当前开发原则

当前阶段遵循：

1. **先跑通全流程**
2. **中间节点只做 smoke 级验证**
3. **召回效果 / 问答效果放到后续专项评估**
4. **不要过早把中间脚本做成生产级测试系统**

也就是说，当前重点不是“把测试写满”，而是把下面这条主链做完整：

```text
source site
  -> fetch
  -> normalize
  -> chunk/schema build
  -> structured support
  -> pg bundles
  -> pg load
  -> app runtime
  -> smoke verify
```

---

## 2. 推荐执行顺序

### 第一步：部署 PG17

```bash
.venv/bin/python scripts/d2_pg_cli.py stage deploy-pg17
```

实际执行：

```bash
bash deploy/pgsql17-ubuntu24/build-and-up.sh
bash deploy/pgsql17-ubuntu24/verify-running.sh
```

### 第二步：先把资产构建出来

如果是完整数据刷新：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-pg-assets
```

如果只是已有数据重建：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-pg-search
```

### 第三步：把资产导入 PostgreSQL

```bash
.venv/bin/python scripts/d2_pg_cli.py load-all --with-vector
```

这一步现在已经支持：

- 本机 `psql`
- 或自动回退到 `docker exec d2-pg17 ... psql`

所以即使宿主机没装 `psql`，也能把流程跑完整。

### 第四步：做 smoke 级联通验证

```bash
.venv/bin/python scripts/d2_pg_cli.py stage smoke-verify
```

它当前只覆盖：

- query execution chain
- postgres runtime ready
- api pg runtime

不会默认跑更慢的 LLM 扩展验证。

---

## 3. 一键跑通完整流程

如果你要从源站一路跑到可用 PG runtime，推荐：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline site-to-live-pg
```

如果你只是在已有资料上做刷新：

```bash
.venv/bin/python scripts/d2_pg_cli.py pipeline refresh-live-pg
```

---

## 4. 当前 CLI 的职责划分

### 4.1 构建型

- `pipeline site-to-chunks`
- `pipeline site-to-pg-assets`
- `pipeline refresh-pg-search`

### 4.2 导入型

- `load-pg`
- `load-dict`
- `load-embeddings`
- `load-strategy`
- `load-all`

### 4.3 验证型

- `stage smoke-verify`
- `stage full-stack-verify`

建议：

- 日常开发默认用 `smoke-verify`
- 需要看 LLM 最终回答时再手动跑 `full-stack-verify`

---

## 5. 当前阶段的测试策略

当前建议把测试分成三层：

### Layer 1：构建成功

检查 bundle 是否能生成、能导入。

### Layer 2：链路联通

检查：

- PG 是否可用
- API 是否可用
- `/qa` 是否能返回 chunks / ranking reasons / source catalog

### Layer 3：效果评估（后续）

后续再专项做：

1. alias / 黑话召回率
2. BM25 + vector 融合效果
3. graph expansion 带来的提升
4. numeric guard 是否抑制幻觉
5. 最终问答引用准确率

当前阶段不建议先把 Layer 3 做得很重。

不过当前仓库已经补了一个**轻量效果评估入口**，用于快速查看“当前版本大概效果”：

```bash
.venv/bin/python scripts/d2_pg_cli.py stage effect-eval
```

产物：

- `docs/tier0/verification/current-pg-effect-eval.json`
- `docs/tier0/verification/current-pg-effect-eval.md`

它不是严格基准测试，而是当前版本的工程化快照。

---

## 6. 当前开发完成度

目前已经补齐到以下程度：

1. PG17 Docker 制品镜像可启动
2. `pgvector + pg_textsearch + pg_trgm + ltree` 可用
3. 主 bundle / dict bundle / embedding bundle / strategy bundle 可构建
4. 资产可导入 PostgreSQL
5. API 可走 PostgreSQL-backed retrieval
6. Query Understanding / rewrite / subquestion plan / ranking reasons 已输出
7. 回答阶段已有 source catalog / verifier release gate

所以当前阶段的重点应转向：

> 跑完整流程 + 稳定数据更新 + 逐步做召回/问答评估

---

## 7. 后续开发优先级

建议优先级如下：

### P1

- 把数据更新流程再固化
- 把更多站点内容规范导入 chunk schema
- 让 `site-to-live-pg` 更稳定

### P2

- 做召回评估集
- 做 alias / numeric / multi-hop 三类专项评测

### P3

- 做 answer quality 与 citation quality 的离线评估
- 再考虑更深的自动化测试

---

## 8. 一句话结论

当前最合理的推进方式不是“先补满测试”，而是：

> 先把 PostgreSQL-only 问答系统的开发流程、导入流程、运行流程完整跑通；中间只做 smoke 校验；等流程稳定后，再专门评估召回效果与问答效果。
