# Blizzhackers `d2data` 数据源评估与接入建议

## 1. 结论

这个数据源 **不是没考虑**，当前仓库里已经纳入了它，但**纳入方式还不够好**。

当前结论分两句：

1. **它很适合做结构化数据底座**
2. **它不适合直接承担“攻略问答文本库”主力角色**

也就是说：

- 对于 **物品 / 符文之语 / 技能 / 场景 / 怪物 / 公式相关** 的精确问答，它很有价值
- 对于 **开荒攻略 / 配装思路 / 打法经验 / 社区问答**，它并不能替代攻略语料

---

## 2. 当前仓库里有没有它

有，而且已经进入当前主数据层。

本地现状（已实际检查）：

- `docs/tier0/merged/normalized/documents.jsonl`
  - `blizzhackers-d2data = 4`
- `docs/tier0/merged/chunks.jsonl`
  - `blizzhackers-d2data = 112`
- `docs/chroma-ready/documents.jsonl`
  - `blizzhackers-d2data = 4`
- `docs/chroma-ready/chunks.jsonl`
  - `blizzhackers-d2data = 112`

所以答案是：

> **当前已经有，但接入质量偏初级，不是最终可用形态。**

---

## 3. 当前接入存在什么问题

### 3.1 当前很多内容更像“目录抓取”，不是“领域实体抓取”

当前本地样本里能看到这类内容：

- `README`
- `root-contents`
- GitHub / API 返回的目录结构
- sitemap / 文件索引片段

这意味着当前接入偏向：

- 把仓库根目录和文件清单当成文本喂进来了

而不是：

- 把真正有价值的 JSON 数据按实体结构拆出来

### 3.2 这会导致两个问题

1. **向量召回噪声大**
2. **GraphRAG 很难直接利用**

因为 GitHub 文件目录、API 列表、sitemap 文本，本身不等于：

- runeword 实体
- unique item 实体
- monster 实体
- area 实体

---

## 4. 这个源最适合给我们补什么

如果你的目标是**社区问答 + 游戏攻略检索**，那 `blizzhackers/d2data` 最适合承担的是：

## 4.1 精确结构化底座

优先级很高：

- Base items
- Unique items
- Set items
- Runes
- Runewords
- Skills
- Monsters
- Areas
- Recipes
- Mercenary / hireling 相关静态数据

这些内容适合转成：

- `canonical_entities`
- `canonical_claims`
- `support_edges`
- `alias_registry`

## 4.2 版本化静态属性层

它的价值在于：

- 更接近游戏原始表结构
- 字段更整齐
- 更适合程序化解析

适合支撑：

- graph facts
- drop / area / skill / item 的严格关系
- 版本差异标注

## 4.3 不适合承担的部分

它不适合直接承担：

- 开荒攻略
- Build 讲解
- 社区经验
- 模糊问答
- 实战技巧

这些仍然更依赖：

- 91D2
- PureDiablo
- Arreat Summit
- 其他中英文攻略页

---

## 5. 对“社区问答能力”来说，它缺了什么

如果你的未来目标是：

> “社区里的问答，只要涉及到游戏攻略的检索都可以做”

那么只靠 `d2data` 还缺三类关键能力：

### A. 攻略文本语料

例如：

- 开荒路线
- build 装备优先级
- 打 Uber 策略
- 地图 farm 建议
- 佣兵搭配经验

### B. 社区黑话 / 俗称映射

例如：

- 军帽
- 超市
- 劳模
- 安头
- 丧钟
- 塔套
- 锤丁

### C. build archetype 结构

例如：

- 锤丁
- 冰法
- 电法
- 新星电法
- 标马
- 弓马
- 狼德
- 陷阱刺客

所以 `d2data` 应该是：

> **精确结构化数据底座**

而不是：

> **社区问答的唯一知识源**

---

## 6. 现在我们应该怎么补

## 6.1 短期建议：保留它，但重做接入方式

当前不要删除它，而是要：

### 从“网页/目录抓取”改成“结构化文件抽取”

推荐做法：

1. 只读取 `json/` 下真正有价值的结构化数据
2. 不再把仓库根目录、API 返回、sitemap 当正文 chunk
3. 按实体类型拆解写入：
   - item
   - rune
   - runeword
   - skill
   - monster
   - area
   - recipe

## 6.2 中期建议：让它进入 graph facts，而不是 guide chunks

推荐把 `blizzhackers-d2data` 的内容优先进入：

- `alias-registry.jsonl`
- `term-equivalence.jsonl`
- `canonical_entities`
- `canonical_claims`
- `build-archetypes` 的支撑字段

而不是优先进：

- 长文本攻略 chunk

## 6.3 长期建议：做 source-role 分工

建议固定：

### `blizzhackers-d2data`
角色：
- **structured_db**
- 精确字段 / 静态规则 / 机器可读数据

### `arreat-summit`
角色：
- **official**
- 老版本官方知识页 / 规则 / 地图 / boss / runeword 文本说明

### `diablo2.io`
角色：
- **structured_db + community reference**
- 大量实体页 + 评论/页面噪声需控制

### `91d2 / PureDiablo`
角色：
- **guide / wiki / community strategy**
- 攻略、开荒、打法经验

---

## 7. 建议你下一步立刻补的能力

如果要让社区问答更强，我建议优先做：

### 1. `blizzhackers-d2data` 结构化重接入

输出目标：

- 重新生成 source-specific structured rows
- 减少噪声 chunk

### 2. `build-archetypes.jsonl` 正式化

把当前 curated build archetype 继续扩：

- 锤丁
- 冰法
- 电法
- 标马
- 弓马
- 狼德
- 召唤死灵
- 陷阱刺客

### 3. 攻略型 chunk 单独分层

把：

- 91D2
- PureDiablo

的攻略内容，明确区分为：

- `guide_section`
- `build_section`
- `mechanic_explainer`

### 4. source-aware rerank

对社区问答非常关键：

- 精确事实优先 structured_db / official
- 攻略问题优先 guide / wiki / forum

---

## 8. 最终判断

### 这个源有没有考虑？

**有，已经接入。**

### 当前都有了吗？

**有一部分，但接入质量还不够。**

### 要不要补充？

**要，而且值得补。**

但补充方式不是继续抓 GitHub 页面文本，而是：

> **把 `blizzhackers/d2data` 当成结构化事实源，重新做定向抽取与规范入库。**

---

## 9. 对你目标最重要的一句话

如果你的终局是：

> “社区里的问答，只要涉及到游戏攻略的检索都可以做，尽可能满足这个能力”

那正确架构应该是：

### `d2data` 负责：

- 精确事实
- 静态字段
- 机器可读规则

### `攻略语料` 负责：

- 开荒建议
- build 思路
- 配装理由
- 实战打法

### `term map + curated anchor` 负责：

- 中文黑话
- 缩写
- 实体归一
- 检索稳定性

三者缺一不可。
