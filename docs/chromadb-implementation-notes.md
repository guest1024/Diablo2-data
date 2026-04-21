# ChromaDB 接入说明

当前项目已确定：

- **向量数据库采用 ChromaDB**

## 推荐导入入口

- `docs/chroma-ready/documents.jsonl`
- `docs/chroma-ready/chunks.jsonl`

## 导入方式

每条记录统一为：

```json
{
  "id": "...",
  "content": "...",
  "metadata": { ... }
}
```

导入 Chroma 时：

```python
collection.add(
    ids=[...],
    documents=[...],
    metadatas=[...]
)
```

注意：

- JSONL 里的 `metadata` 保留统一规范结构
- 真正写入 Chroma 时，需要把 list / dict / null 做一次标量化转换
- 当前 `app/chroma_store.py` 已经处理了这一步

## 为什么这样设计

1. 不把 embedding 写死在主数据文件里
2. 方便以后切换 embedding 模型
3. 兼容 Chroma 的 `ids / documents / metadatas` 结构
4. 更适合后续中英文混合检索

## 推荐索引层

### collection 1：entity collection
- 输入：canonical entity card
- 用途：实体定位

### collection 2：evidence collection
- 输入：chunk
- 用途：证据召回

## 当前最推荐导入数据

优先导入：
- `docs/chroma-ready/chunks.jsonl`

如果要做 entity 定位，再导入：
- `docs/chroma-ready/documents.jsonl`

## 当前第一版系统的 embedding 策略

当前第一版为了保证：

- 本地可复现
- 不依赖额外模型下载
- 先把开发底座跑通

采用的是：

- **local hashing embedding baseline**

这不是最终生产 embedding，只是第一版工程底座。

后续升级建议：

1. 开发阶段先保持当前 baseline 跑通全链路
2. 第二阶段切换到多语言 embedding（如 BGE-M3）
3. 第三阶段再叠加 reranker / GraphRAG 查询层
