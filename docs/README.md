# Diablo II 知识库 / GraphRAG 项目说明

这份文档面向你后续**自己逐步开发和测试**，只保留最重要的建设路线、实施步骤、架构选型原因和常见问题。

---

## 1. 项目目标

建设一套可持续扩充的 Diablo II / LoD / D2R 知识库，用于：

1. **全文检索 / RAG**
2. **图谱检索 / GraphRAG**
3. **中英文混合问答**
4. **后续 Agent 工具调用**

当前项目已经完成：

- 基础抓取
- 高价值详情页抓取
- PureDiablo 高价值补充
- 91D2 中文高价值补充
- merged 主知识层
- graph / csv / export bundle / handoff / quickstart / query recipes
- Chroma-ready 统一数据包
- 第一版可运行问答底座（FastAPI + Chroma + local graph + OpenAI-compatible LLM）

后续开发重点是：**把这些结果真正接成可问答系统**。

当前第一版系统快速入口：

- `docs/first-system-quickstart.md`
- `scripts/smoke_test_first_system.py`
- `docs/tier0/curated/`
- `docs/tier0/verification/README.md`

---

## 2. 最终主入口

以后你开发时，优先只看：

### 主数据层
- `docs/tier0/merged/normalized/documents.jsonl`
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`

### 导出层
- `docs/tier0/merged/export-bundle.json`
- `docs/tier0/merged/csv/manifest.json`

### 说明层
- `docs/tier0/merged/CONSUMER-GUIDE.md`
- `docs/tier0/merged/QUICKSTART.md`
- `docs/tier0/merged/HANDOFF.md`
- `docs/tier0/query-recipes.md`
- `docs/tier0/bilingual-term-map.json`
- `docs/data-spec-v1.md`
- `docs/tier0/bilingual-graphrag-guidelines.md`
- `docs/中英实体映射与知识图谱建设手册.md`
- `docs/tier0/blizzhackers-d2data-source-assessment.md`
- `docs/社区问答能力缺口与补强方案.md`

---

## 3. 架构选型

## 3.1 为什么采用“文本层 + 图层”双轨

原因：

- 纯向量检索适合找“相似文本”
- 纯图谱适合找“明确关系”
- Diablo II 既有：
  - item / skill / rune / runeword / area / monster 这种结构化知识
  - 又有 build / FAQ / 攻略 / 经验这种半结构化知识

所以最合理的方案不是二选一，而是：

### 文本层
负责：
- chunk 检索
- 证据正文
- FAQ / build / 经验内容

### 图层
负责：
- 实体定位
- 关系扩展
- source / version / conflict 约束

---

## 3.2 为什么 `merged/` 作为主入口

原因：

- base 层比较干净，但覆盖有限
- high-value / purediablo 层有更高信息密度
- merged 层已经把多来源合并到一个主结果里

所以后续生产问答默认应以：
- `docs/tier0/merged/`

作为主入口。

---

## 3.3 为什么 canonical id 语言无关

原因：

- 中文名、英文名、俗称、缩写都可能变化
- 若直接拿语言文本做主键，会导致：
  - 中英文不统一
  - 别名难合并
  - 版本难治理

所以主键必须是：
- `canonical_id`

而不是：
- 中文标题
- 英文标题

---

## 3.4 为什么 alias 比 embedding 更重要

原因：

暗黑 2 的问答里大量失败都不是因为 embedding 弱，而是因为：

- 中文问法和英文知识不一致
- 军帽 / Harlequin Crest
- 精神 / Spirit
- 地穴 / The Pit
- 火炬 / Hellfire Torch

所以必须先把：
- alias
- 术语映射
- 缩写
- 中文俗称

做扎实，再调 embedding。

---

## 3.5 为什么 chunk 不能只按长度切

因为 Diablo II 是强结构化领域。

错误做法：
- 纯 512 / 1024 token 固定切块

正确做法：
- 按知识对象切
  - item
  - skill
  - recipe
  - build section
  - FAQ section

这样检索质量更高。

---

## 4. 实施步骤（推荐顺序）

## Phase 1：冻结规范

先把规范固定，不要边做边改。

必读：
- `docs/data-spec-v1.md`
- `docs/tier0/bilingual-graphrag-guidelines.md`

目标：
- 明确 documents / chunks / canonical_entities / canonical_claims / provenance 字段
- 明确 alias / version / contradiction 规则

---

## Phase 2：清点并确认当前数据主入口

只确认 merged 主层：

- `merged/normalized/documents.jsonl`
- `merged/chunks.jsonl`
- `merged/canonical-entities.jsonl`
- `merged/canonical-claims.jsonl`
- `merged/provenance.jsonl`

目标：
- 后续所有开发都基于 merged，不再分散看 base / high-value / purediablo

---

## Phase 3：构建检索索引

你后续真正开发时，先做这两类索引：

### A. entity 索引
输入：
- canonical name
- aliases
- node_type
- short summary

输出：
- entity lookup index / embedding

### B. evidence 索引
输入：
- chunks
- source
- authority
- version
- language

输出：
- 向量索引 / BM25 / 混合索引

目标：
- query 先找实体，再找证据

---

## Phase 4：构建图数据库或图缓存

最推荐：
- Neo4j

原因：
- 上手快
- 适合 property graph
- 容易调试
- 可以直接做关系扩展和 provenance 查询

参考：
- `docs/tier0/merged/NEO4J-PLAYBOOK.md`

目标：
- 把 merged nodes / edges / claims / chunks 接入图数据库

---

## Phase 5：实现问答检索链路

推荐固定流程：

1. 语言识别
2. alias 扩展
3. canonical entity 定位
4. 图扩展
5. canonical claims 检索
6. provenance grounding
7. chunk 召回
8. authority / version / language rerank
9. 生成答案

---

## Phase 6：做评测

最少准备：
- 50 条中文问句
- 50 条英文问句

覆盖：
- item
- runeword
- skill
- monster / area
- quest
- build / FAQ
- 版本差异

目标：
- 看 alias 命中率
- 看 entity 命中率
- 看 evidence grounding 是否正确

---

## Phase 7：继续补数据

优先补：
1. 91D2
2. TTBN
3. 中文 FAQ / build / 地图 / 掉落
4. 版本差异资料

---

## 5. 推荐技术路线

## 路线 A：先做可用原型

适合你想快速跑起来。

步骤：
1. merged jsonl + chunks 建本地检索
2. alias lookup
3. canonical claims + provenance 做 grounding
4. LLM 生成答案

优点：
- 快
- 易调试

缺点：
- 图能力还不强

---

## 路线 B：先做 GraphRAG 主线

步骤：
1. Neo4j 接入 merged graph
2. 构建 graph neighborhood retrieval
3. chunk 作为证据补充
4. 版本和冲突进入排序

优点：
- 结构化问答强
- 版本/来源控制更好

缺点：
- 实现更重

---

## 路线 C：双轨并行（推荐）

1. 先搭文本检索原型
2. 同时导入 Neo4j
3. 最后把图检索和文本检索融合

原因：
- 这是最稳的路线
- 文本层能快速出效果
- 图层能逐步增强复杂问答

---

## 6. 架构选型建议

## 6.1 存储

### 文本层
- JSONL 文件本地维护
- 后续可切换对象存储 / 数据库

### 图层
- Neo4j 优先

### 向量层
- 单独 embedding store
- 不建议和图层强耦合

---

## 6.2 检索

最少三路：
- alias / exact match
- lexical / BM25
- vector search

GraphRAG 再加：
- graph neighborhood expansion

---

## 6.3 排序

排序必须至少考虑：
- authority_tier
- source
- language fit
- version fit
- supporting_source_count

---

## 6.4 输出

答案最好固定包含：
- 结论
- 适用版本
- 中英文术语
- 证据来源
- 冲突说明（如果有）

---

## 7. 常见问题解答

### Q1：我后续只看哪个目录？
A：`docs/tier0/merged/`

### Q2：我后续只看哪些文件？
A：
- `canonical-entities.jsonl`
- `canonical-claims.jsonl`
- `provenance.jsonl`
- `chunks.jsonl`
- `export-bundle.json`

### Q3：为什么不用纯向量库？
A：因为 Diablo II 有大量结构化关系，纯向量检索不够稳。

### Q4：为什么不能直接把中文名当主键？
A：因为中英文、俗称、缩写会冲突，后续无法长期维护。

### Q5：为什么不先抓更多再说？
A：可以抓，但不先冻结规范，后面会重构成本很高。

### Q6：现在中文问答效果够好吗？
A：还不够。当前更像“英文知识底座 + 中文查询入口”。

### Q7：下一步最值的是啥？
A：先接 merged 主层做原型问答，再补中文高质量内容。

---

## 8. 最后的建议

你后续自己开发时，不要被中间层干扰。

### 只记住：
1. **主入口是 `merged/`**
2. **规范看 `data-spec-v1.md`**
3. **流程看 `production-flow.md`**
4. **中英文细则看 `bilingual-graphrag-guidelines.md`**

### 最推荐的落地顺序：
1. 先把 merged 接成一个可问答原型
2. 再做评测
3. 再补中文高质量源
4. 再增强 graph 关系和版本治理
