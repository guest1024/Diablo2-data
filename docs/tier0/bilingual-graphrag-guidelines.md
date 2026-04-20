# 中英文混合检索 / GraphRAG 构建准则

这份文档面向当前暗黑 2 知识库流水线，重点回答：

- 中英文混合语料该怎么组织
- embedding 该怎么切
- Graph 该怎么建
- 检索、重排、问答时要抓哪些细节

## 1. 先定一个核心原则：**实体主键语言无关**

不要让中文名或英文名直接成为主键。

应当用：

- `canonical_id`
- `entity_type`
- `game_variant`
- `patch/version`

来标识一个实体。

例如：

- `Runeword:spirit`
- `UniqueItem:harlequin_crest`
- `Area:pit_level_1`

中文、英文、俗称、缩写都只作为 **alias**。

## 2. 语言层必须分开存，但检索层必须能联动

每条知识至少保留：

- 原始语言文本
- `language`
- 原始标题
- alias 列表
- source / authority / variant / patch

推荐字段：

```json
{
  "canonical_id": "...",
  "language": "zh|en",
  "title": "...",
  "aliases": ["...", "..."],
  "body": "...",
  "source_id": "...",
  "authority_tier": "...",
  "game_variant": "classic|lod|d2r",
  "version_tokens": ["1.13", "2.4"]
}
```

原则：

- **存储时分语言**
- **检索时跨语言打通**

## 3. Alias 比 embedding 更重要

像暗黑 2 这种强术语领域，很多检索失败不是 embedding 不够强，而是：

- 用户用中文俗称
- 资料是英文正式名
- 论坛用缩写/简称
- 版本前后叫法不同

因此必须优先建设：

- 中文名
- 英文名
- 官方译名
- 社区俗称
- 缩写
- 版本别名

例如：

- `Spirit` / `精神`
- `Harlequin Crest` / `军帽`
- `The Pit` / `地穴`
- `Hellfire Torch` / `地狱火炬`

实践上：

- **query 先做 alias expansion**
- 再做 embedding 检索

## 4. Chunk 不要只按长度切，要按“知识对象”切

最差的做法是纯 512 / 1024 token 固定切块。

更适合暗黑 2 的切法：

### 4.1 实体页

一个实体一张卡片：

- item
- runeword
- skill
- monster
- area
- quest

如果内容太长，再按字段切：

- summary
- stats
- requirements
- drop/source
- notes
- version differences

### 4.2 攻略页

按语义段切：

- build summary
- skill plan
- gear
- merc
- farming route
- strengths / weaknesses

### 4.3 论坛/社区页

不要整帖直接喂 embedding。

应拆成：

- 结论段
- FAQ 段
- 数据表段
- 经验总结段

## 5. Embedding 要分“实体检索”和“证据检索”

建议至少两类向量对象：

### A. entity-card embeddings

用于“Spirit 是什么”“军帽是什么”这种实体定位。

输入应短而结构化，例如：

- title
- aliases
- entity type
- short summary

### B. evidence-chunk embeddings

用于“给我出处”“这个 build 怎么玩”“这个机制怎么解释”。

输入应是：

- 正文 chunk
- 保留 source / authority / patch / language 元数据

这样做比“所有文本一套 embedding”效果好。

## 6. 混合检索时，至少做三路召回

推荐召回结构：

1. **alias / exact match**
2. **BM25 / lexical**
3. **embedding / semantic**

GraphRAG 场景再加：

4. **graph neighborhood recall**

即：

- 先找实体
- 再扩邻居
- 再找证据 chunk

## 7. Graph 里最值得先建的节点

对暗黑 2 来说，优先级最高的是：

- `Runeword`
- `UniqueItem`
- `SetItem`
- `BaseItem`
- `Rune`
- `Recipe`
- `Skill`
- `Class`
- `Monster`
- `Area`
- `Quest`
- `NPC`
- `Patch`
- `SourceDocument`

## 8. Graph 里最值得先建的边

第一批就够用的边：

- `ALIASES`
- `DESCRIBES`
- `BELONGS_TO_SOURCE`
- `USES_RUNE`
- `REQUIRES_BASE`
- `DROPS_IN`
- `USED_BY_BUILD`
- `BELONGS_TO_CLASS`
- `SUPPORTED_BY_SOURCE`
- `EVIDENCED_BY`
- `OVERRIDES_IN_PATCH`
- `CONTRADICTS`

不要一开始就建太多花哨边；先保证问答最常见路径可走通。

## 9. 版本和语言必须进排序，不只是进存储

检索排序时至少要考虑：

- query 语言
- source 语言
- game variant 是否匹配
- patch/version 是否匹配
- authority tier
- supporting_source_count

例如用户问：

- “D2R 精神盾需要什么底材”

就不该把 LoD 旧资料排在最前面。

## 10. 中英文混合问答的推荐流程

### Step 1: 语言识别

- query 是中文 / 英文 / 混合

### Step 2: alias 扩展

- 中文别名 → canonical_id
- 英文别名 → canonical_id

### Step 3: 实体召回

- entity-card embedding
- lexical + alias

### Step 4: 图扩展

- 邻居实体
- 相关 claim
- 相关 provenance

### Step 5: 证据召回

- evidence chunk retrieval

### Step 6: 排序

按：

- authority
- language fit
- version fit
- graph support
- chunk relevance

### Step 7: 生成答案

输出：

- 结论
- 适用版本
- 中英文术语
- 引用来源
- 若有冲突则标明冲突

## 11. 最容易踩的坑

### 坑 1：把 sitemap / 索引页当正文

这会让 embedding 被目录噪音污染。

### 坑 2：中文译名只做字符串翻译，不做 alias

会导致跨语言召回很差。

### 坑 3：图里没有 patch/version

会导致不同版本机制混在一起。

### 坑 4：论坛帖和官方页同权

会导致答案不稳定。

### 坑 5：chunk 只按长度切

会让 item/build/recipe 问题召回不准。

## 12. 当前仓库最推荐的下一步

结合当前已经有的产物，优先顺序建议是：

1. 给 merged 图层补 canonical / provenance 级联
2. 给高价值详情页补 alias / canonical claims
3. 对 `diablo2-io` 页面做“正文去论坛噪音”清洗
4. 做 zh/en 交叉评测集
5. 再扩 Tier 1 来源

## 13. 最实用的一句话建议

对中英文混合 GraphRAG：

**先把 entity canonicalization + alias 做对，再谈 embedding 调优；先把 source / version / provenance 做对，再谈生成质量。**
