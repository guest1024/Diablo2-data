# Diablo II 知识库缺口评估（按问答类型）

这份文档的目的不是重复统计总量，而是回答：

- 当前知识库**已经足够回答什么问题**
- 哪些问题类型还**明显不足**
- 后续优先该补什么数据

参考当前本地结果：

- 合并总字符数：`9,394,062`
- 合并 chunk surfaces：`8,594`
- merged graph：`1074 nodes / 1197 edges / 879 claims`

---

## 1. 评估标准

按 5 档判断：

- `A`：当前已经比较够用
- `B`：可用，但仍需补充
- `C`：部分可答，稳定性一般
- `D`：明显不足
- `E`：几乎没有覆盖

---

## 2. 当前问答能力评估

| 问答类型 | 当前评级 | 说明 |
| --- | --- | --- |
| 装备 / 符文之语 / 套装 / 底材 | A | `diablo2.io + Arreat + PureDiablo` 覆盖已较强，高价值详情页也较多 |
| 技能 / 职业树 / 职业概览 | A- | 英文覆盖较强，中文可通过 alias + 英文证据支撑 |
| 怪物 / 区域 / 地图 / 任务基础 | B+ | 已有场景、怪物、任务资料，但仍可继续扩充详情页 |
| Cube / Recipe / FAQ / 基础机制 | B+ | 已有 Horadric Cube、常见问题、基础知识，但中文机制层还偏薄 |
| 中文 FAQ / 中文新手问答 | C+ | 已有 91D2 补强，但中文主库仍偏薄 |
| Build / 开荒 / MF 路线 | C | 已有一些经验帖和 build，但覆盖还不够系统化 |
| 掉落 / TC / 物价 / 交易价值 | C- | 有一部分素材，但结构化程度不够，很多是散在正文中 |
| 版本差异 / Patch 行为 | C- | 已有 version tags / contradiction seeds，但还不够稳定支撑严谨问答 |
| 中文纯问答闭环（不靠英文） | D | 中文内容还远不够成为主知识底座 |
| 多跳图推理（复杂机制链路） | D | 图谱已有骨架，但关系密度和 claim 细粒度仍不足 |

---

## 3. 当前“已经足够”的问题

以下问题类型已经比较适合直接做原型问答：

### 3.1 装备类
- Spirit 是什么
- Enigma 需要哪些符文
- 军帽 / Harlequin Crest 是什么
- Hellfire Torch 有什么用途
- 某个 Unique / Set / Base Item 的核心属性

### 3.2 技能 / 职业类
- Blizzard 是什么技能
- Paladin Defensive Auras 是什么
- Necromancer Poison and Bone 是什么体系
- Barbarian Warcries 有什么特点

### 3.3 地图 / 任务 / 基础知识类
- The Pit / 地穴 是什么区域
- Den of Evil 是什么任务
- Horadric Cube 能做什么
- 常见新手问题、开荒常见问题

---

## 4. 当前“不够稳定”的问题

这些问题现在可以尝试回答，但不建议直接当生产级结果：

### 4.1 Build / 路线类
- 冰法开荒怎么配
- MF 路线如何规划
- 某职业从开荒到毕业怎么成长

原因：
- 资料分散
- 中文经验层不够厚
- 缺少统一 build schema

### 4.2 版本差异类
- LoD 和 D2R 某机制有什么差异
- 某公式 / 某掉落在不同版本是否一致

原因：
- 已有版本标签，但 claim 还不够细
- contradiction 还只是 seed

### 4.3 掉落 / 物价 / 市场类
- 某装备值不值钱
- 某场景掉率高不高
- 哪些区域最适合刷某类装备

原因：
- 缺少稳定结构化 drop / value 层
- 论坛/市场噪音很高

---

## 5. 当前最明显的缺口

### 5.1 中文主语料仍然不足

虽然已经有：
- `91d2-high-value`

但中文量级依旧明显弱于英文主库。

结论：
- 当前更适合 **中文问句 -> alias 映射 -> 英文证据召回 -> 中文答案生成**
- 不适合纯中文主语料闭环

### 5.2 Build / FAQ / route 还不够结构化

现在很多 build / 经验 / FAQ 仍然在长文里，  
没有被提升为稳定 schema，例如：

- build_summary
- skill_plan
- gear_plan
- merc_plan
- route_plan

### 5.3 掉落 / TC / 版本差异缺少强结构化

当前图谱里：
- entity / claim / provenance 已有

但还缺：
- `DROPS_IN`
- `USES_RUNE`
- `REQUIRES_BASE`
- `OVERRIDES_IN_PATCH`
- `CONTRADICTS`

这些关系的高密度建设。

---

## 6. 后续最值得补的数据

### P1：最应该补
1. 中文高质量资料站（继续扩 91D2 / TTBN）
2. 高价值详情页继续扩展
3. Build / FAQ / route 专项语料
4. 掉落 / TC / 区域效率资料

### P2：结构化增强
5. 版本差异专门数据
6. claim 粒度更细
7. graph relation 更强

### P3：生产级评测
8. 中文 / 英文混合问答评测集
9. retrieval / rerank 评测

---

## 7. 推荐下一步（按产出比）

如果后续只做 3 件事，建议：

### 1. 继续补中文高质量源
优先：
- `91d2.cn`
- `ttbn.cn`

### 2. 把 build / FAQ / route 做成结构化 chunk
不要只保留长文。

### 3. 补 graph 关系
优先做：
- `USES_RUNE`
- `REQUIRES_BASE`
- `DROPS_IN`
- `OVERRIDES_IN_PATCH`

---

## 8. 总结

一句话结论：

> 当前知识库已经足够支撑一个 **可用的 Diablo II 原型级 RAG / GraphRAG 系统**，尤其擅长装备、符文之语、技能、基础地图任务问题；但若要支撑更稳定的中英双语问答、build 路线问答、版本差异问答，还必须继续补中文高质量语料、结构化 build/FAQ 数据，以及更细粒度的图谱关系。  
