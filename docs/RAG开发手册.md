# Diablo II RAG 开发手册

这份手册面向开发者，回答三件事：

1. 当前有哪些数据
2. 这些数据分别适合做什么
3. 现在已经能解决哪些 RAG / GraphRAG 问题，哪些还不能

---

## 1. 当前数据层总览

## 1.1 merged 主知识层

主入口：

- `docs/tier0/merged/normalized/documents.jsonl`
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`

### 性质

- 主生产入口
- 中英混合主语料
- 面向检索和图谱联合使用

### 适合做

- 主 RAG 召回
- 主 GraphRAG grounding
- 来源追溯

---

## 1.2 chroma-ready 包

入口：

- `docs/chroma-ready/documents.jsonl`
- `docs/chroma-ready/chunks.jsonl`
- `docs/chroma-ready/manifest.json`

### 性质

- 面向向量库导入
- 不内嵌 embedding
- 统一 schema

### 适合做

- Chroma / 向量数据库导入
- 证据 chunk 检索

---

## 1.3 curated anchor 层

入口：

- `docs/tier0/curated/documents.jsonl`
- `docs/tier0/curated/chunks.jsonl`

### 性质

- 面向中文黑话 / 缩写 / 社区俗称
- 不是大规模正文库
- 是“稳定召回层”

### 适合做

- 术语归一
- 中文 query 稳定直达
- community query first-hit stabilization

---

## 1.4 term / alias / build 支撑层

入口：

- `docs/tier0/bilingual-term-map.json`
- `docs/tier0/alias-registry.jsonl`
- `docs/tier0/term-equivalence.jsonl`
- `docs/tier0/build-archetypes.jsonl`

### 性质

- 图谱友好
- 检索友好
- 不是原文证据，而是“结构化支撑资产”

### 适合做

- query expansion
- alias resolution
- build archetype retrieval
- graph import

---

## 2. 当前架构怎么理解

当前推荐理解为四层：

### Layer 1：Query Understanding

负责：

- term map expansion
- alias normalization
- acronym expansion

### Layer 2：Retrieval

负责：

- curated anchor 直达
- lexical search
- vector search
- source-aware ranking

### Layer 3：Graph Grounding

负责：

- canonical entity
- claim / provenance
- patch / version awareness

### Layer 4：Answering

负责：

- 证据组织
- 最终回答生成
- 来源呈现

---

## 3. 当前已经能解决哪些问题

### A. 百科词典类问题

已经比较稳：

- Spirit 是什么
- 军帽是什么
- 火炬是什么
- 乔丹是什么
- 无限是什么
- 安头 / 蛛网 / 年纪 / 基德 / 格里芬 等装备黑话

### B. 地图 / 场景 / Boss 黑话

已经比较稳：

- 超市
- 劳模
- 大菠萝
- 牛场
- 古代通道
- 尼拉塞克
- 老P

### C. Build archetype / 职业简称

当前已具备初步能力：

- 锤丁
- 冰法
- 电法
- 新星电法
- 标马
- 弓马
- 狼德
- 陷阱刺客
- 召唤死灵

### D. 社区缩写

当前已具备初步能力：

- SOJ
- CTA
- COH
- BOTD
- HOTO
- ULC
- USC
- MF
- DClone

---

## 4. 当前还不够强的地方

### A. 机制计算

还缺：

- FCR/FHR/FBR/IAS breakpoint 结构化层
- combat formula 层
- drop / TC / qlvl / mlvl / MF 结构化层

### B. 攻略型回答

还缺：

- build schema 更细化
- gear / merc / route / progression 拆层

### C. patch / 版本差异

还缺：

- 版本差异 facts 更强结构化
- patch-aware relation 更丰富

---

## 5. 当前推荐的开发顺序

### 第一步：优先补结构化支撑资产

- `alias-registry.jsonl`
- `term-equivalence.jsonl`
- `build-archetypes.jsonl`
- `graph-schema-v1.md`

### 第二步：补机制层

- `breakpoints.jsonl`
- `combat-formulas.jsonl`
- `cube-recipes.jsonl`
- `mercenaries.jsonl`

### 第三步：补攻略层

- `farm-routes.jsonl`
- `uber-events.jsonl`
- build gear plan / merc plan / progression plan

---

## 6. 当前验证怎么看

优先看：

- `docs/tier0/verification/verification-index.md`
- `docs/tier0/verification/verification-suite.md`
- `docs/tier0/verification/routing-matrix.md`
- `docs/tier0/verification/surface-coverage-report.md`

如果你只想快速确认当前底座健康度：

```bash
source .venv/bin/activate
python scripts/verify_first_system_stack.py
```

---

## 7. 当前一句话判断

当前这套底座已经足够做：

- 词典型 RAG
- 中英黑话映射
- 稳定 community query 检索
- 初步 GraphRAG

但如果要进一步做“更强的社区攻略问答”，下一步必须补：

> **机制层 + build schema 层 + 版本差异层。**
