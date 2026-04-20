# Diablo II 数据获取与处理：最终生产流程

如果你只关心**最终结果**，以后只需要记住下面 4 步。

## 第 1 步：抓取

运行：

```bash
python3 scripts/run_production_pipeline.py
```

它会自动：

- 跑基础 Tier 0 抓取
- 扩高价值详情页
- 补 PureDiablo / 高价值正文
- 生成 merged 图层
- 导出 merged CSV
- 刷新统计 / 文档 / 清单

## 第 2 步：验收

运行：

```bash
python3 scripts/verify_production_pipeline.py
```

它会确认：

- merged bundle 存在
- merged CSV 存在
- merged docs 存在
- combined chars / chunk 数达到预期

## 第 3 步：只看最终结果

以后优先看这些文件：

### 文本检索
- `docs/tier0/merged/chunks.jsonl`
- `docs/tier0/merged/normalized/documents.jsonl`

### 图谱问答
- `docs/tier0/merged/canonical-entities.jsonl`
- `docs/tier0/merged/canonical-claims.jsonl`
- `docs/tier0/merged/provenance.jsonl`

### 导出接入
- `docs/tier0/merged/export-bundle.json`
- `docs/tier0/merged/csv/manifest.json`
- `docs/tier0/merged/NEO4J-PLAYBOOK.md`

### 使用说明
- `docs/tier0/merged/CONSUMER-GUIDE.md`
- `docs/tier0/merged/QUICKSTART.md`
- `docs/tier0/merged/HANDOFF.md`
- `docs/tier0/query-recipes.md`
- `docs/tier0/bilingual-graphrag-guidelines.md`

### 内容规模
- `docs/tier0/combined-content-stats.md`
- `docs/tier0/high-value/README.md`

## 第 4 步：问答构建准则

只记住这几条：

1. **canonical id 不要用中文/英文名，语言无关**
2. **alias 比 embedding 调优更重要**
3. **chunk 按知识对象切，不要纯按长度切**
4. **排序一定考虑 authority / language / version**
5. **最终优先使用 merged 层做检索和图谱问答**

## 现在的推荐主入口

如果你后续直接接 GraphRAG / Agent：

- 主图层：`docs/tier0/merged/`
- 主说明：`docs/tier0/merged/CONSUMER-GUIDE.md`
- 主导出：`docs/tier0/merged/export-bundle.json`
