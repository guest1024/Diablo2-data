# 第一版系统快速启动

当前仓库已经具备一个可直接开发的 **Diablo II 中英文 GraphRAG 第一版底座**：

- API：FastAPI
- 向量库：ChromaDB
- 图约束：`docs/tier0/merged/`
- LLM：OpenAI-compatible 接口
- 当前默认 embedding：**本地 hashing baseline**
  - 原因：零外部模型下载、可复现、适合作为开发底座
  - 后续生产建议再切换到多语言 embedding（如 BGE-M3）

---

## 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. 重建统一数据包

如果你前面又补充了新数据，先重建 merged normalized 和 Chroma-ready 包：

```bash
python scripts/build_merged_normalized.py
python scripts/build_chroma_package.py
python scripts/verify_chroma_package.py
```

当前验证通过后的关键规模：

- merged normalized documents：`455`
- merged chunks：`8652`
- chroma-ready documents：`455`
- chroma-ready chunks：`8652`
- runtime curated anchor documents：`56`
- runtime curated anchor chunks：`56`

---

## 3. 启动服务

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
```

默认接口：

- `GET /health`
- `POST /ingest`
- `POST /qa`

---

## 4. 导入 Chroma

```bash
curl -X POST http://127.0.0.1:8000/ingest
```

期望返回：

```json
{
  "documents": 511,
  "chunks": 8708
}
```

说明：

- `docs/chroma-ready/` 仍是主包：`455 / 8652`
- 系统在导入时会自动追加 `docs/tier0/curated/` 下的 56 张本地锚点卡
- 因此运行时 Chroma 总量是 `511 / 8708`

---

## 5. 提问示例

### 只看检索结果

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H 'Content-Type: application/json' \
  -d '{"query":"Spirit 是什么？","use_llm":false}'
```

### 走完整问答

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H 'Content-Type: application/json' \
  -d '{"query":"What is Hellfire Torch?","use_llm":true}'
```

---

## 6. 一键烟雾测试

```bash
source .venv/bin/activate
python scripts/verify_bilingual_term_map.py
python scripts/verify_curated_anchor_routing.py
python scripts/verify_routing_matrix.py
python scripts/verify_curated_surface_alignment.py
python scripts/build_verification_index.py
python scripts/build_curated_catalog.py
python scripts/build_term_map_catalog.py
python scripts/verify_strategy_docs.py
python scripts/verify_first_system_stack.py
python scripts/smoke_test_first_system.py --with-llm
```

这会验证：

1. `/health`
2. `/ingest`
3. 中文 / 英文查询的基础召回
4. LLM 回答链路

---

## 7. 当前实现细节

### 7.1 图数据入口

- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`
- `docs/tier0/merged/aliases.jsonl`

### 7.2 向量数据入口

- `docs/chroma-ready/documents.jsonl`
- `docs/chroma-ready/chunks.jsonl`

### 7.3 检索策略

当前 `/qa` 采用三段式：

1. entity resolve
2. Chroma vector retrieval
3. lexical / entity-linked 补强

这意味着它已经不是纯向量检索，而是一个适合继续扩展成 GraphRAG 的可运行底座。

---

## 8. LLM 配置说明

当前代码同时兼容两套环境变量命名：

- `LLM_API_KEY / LLM_BASE_URL / LLM_MODEL`
- `OPENAI_API_KEY / BASE_URL / MODEL`

例如：

```bash
export OPENAI_API_KEY="<your-key>"
export BASE_URL="https://vibediary.app/api/v1"
export MODEL="gpt-5.4"
```

项目会自动把 base URL 规范化到 `/v1` 形式，因此你可以直接给兼容 OpenAI 的 endpoint。

如果你使用本地 `.env.local`，也可以同时写入 `LLM_*` 与 OpenAI 风格变量，方便脚本和服务共享。

---

## 9. 当前能力边界

### 已验证可用

- 英文实体问答：`Hellfire Torch`
- 中英混合问答：`Spirit 是什么？`
- 中文词面召回：`军帽是什么？`

### 当前仍需后续增强

- 中文俗称 -> 英文 canonical alias 的覆盖还不够全
- 例如：
  - `精神符文之语`
  - `军帽 -> Shako`
  - `地穴 -> The Pit`
- 这些更适合在 **alias lexicon / bilingual term map** 阶段系统补齐

当前仓库已内置第一版术语映射表：

- `docs/tier0/bilingual-term-map.json`
- `docs/tier0/curated/`

服务会在检索前自动做 query expansion，但这只是第一版人工词典；后续应继续扩充。

---

## 10. 推荐的下一步

如果你下一步开始正式开发，建议顺序如下：

1. 固化 alias lexicon
2. 把当前 hashing embedding 换成多语言 embedding
3. 增加 BM25 / hybrid retrieval
4. 把 canonical entity / claims 接成图查询层
5. 加 reranker
6. 再做正式 GraphRAG pipeline

对应方案文档：

- `docs/中英文混合GraphRAG技术方案.md`
- `docs/中英文混合GraphRAG实施方案.md`
- `docs/最小问答原型设计.md`

补充验证材料：

- `docs/tier0/verification/first-system-query-eval.md`
- `docs/tier0/verification/manual-gap-check-2026-04-21.md`
- `docs/first-system-flow-and-code.md`
- `docs/ralph-handoff-2026-04-22.md`
- `docs/tier0/evals/llm-generated-query-eval-dataset.json`

### 11. 生成 LLM Eval Dataset 并跑评测

```bash
python scripts/generate_llm_eval_dataset.py
python scripts/evaluate_llm_generated_dataset.py
python scripts/evaluate_llm_generated_dataset.py --use-llm
python scripts/verify_llm_eval_dataset_grounding.py
```

说明：

- 第一步：用当前配置的大模型，**基于仓库内 Diablo2 语料证据** 生成一组小型评测 query dataset
- 第二步：评估规则/检索链路
- 第三步：评估启用 LLM 的完整问答链路

当前 dataset 不再是通用问答 prompt 随机出题，而是会显式引用：

- `docs/tier0/curated/chunks.jsonl`
- `docs/chroma-ready/chunks.jsonl`

因此它更适合验证：

- Diablo2 俗称 / 黑话路由
- facet-aware 的多路召回 query rewrite
- 子问题分解是否和真实语料对齐

当前默认覆盖 **25 条 source-grounded case**，包含：

- 物品 / 符文之语简称：`Spirit / HOTO / CTA / SOJ / Infinity`
- 黑话 / 区域：`超市 / 劳模 / 牛场 / 古代通道 / 地穴`
- build / 玩法：`新星电法 / ES / Memory / Infinity Scythe`
