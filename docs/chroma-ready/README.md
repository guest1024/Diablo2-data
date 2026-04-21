# ChromaDB 就绪数据包

- Documents: `455`
- Chunks: `8652`
- Vector DB: `ChromaDB`

说明：

- 这是主 Chroma-ready 数据包规模
- 第一版运行时系统还会自动追加 `docs/tier0/curated/` 下的 56 张本地锚点卡
- 因此实际服务导入后的总量为：`511 documents / 8708 chunks`

推荐导入方式：

1. 读取 `documents.jsonl` / `chunks.jsonl`
2. 提取 `id / content / metadata`
3. 用 Chroma collection.add(ids=..., documents=..., metadatas=...) 导入
