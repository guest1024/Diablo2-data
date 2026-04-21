# 下一轮数据补充优先级（执行版）

这份文档把“后续该补哪些数据”进一步压缩成**可执行优先级**，方便下一轮继续抓取。

---

## P0：立即补（最高收益）

## 1. 中文高质量资料页

### 1.1 91D2
目标：
- 再补 `角色职业`
- 再补 `新手指引`
- 再补 `任务攻略`
- 再补 `场景地图`

建议追加量：
- 每个栏目再抓 `15~30` 页

为什么：
- 中文 build / FAQ / 开荒内容直接提升中文问答质量

### 1.2 TTBN
目标：
- 装备大全
- 地图场景
- FAQ / 雇佣兵
- 掉落 / TC / 常用资料合集

建议追加量：
- 首批抓 `20~50` 页

为什么：
- 中文资料库属性强，适合作为主补强源

---

## 2. 英文高价值详情页

### 2.1 diablo2.io
优先扩：
- runewords
- uniques
- sets
- skills
- monsters
- areas
- recipes
- base items

建议追加量：
- 每类再扩 `20~100` 页

### 2.2 Arreat Summit
优先扩：
- skills 子页
- items 子页
- monsters 子页
- quests / rewards

建议追加量：
- 再扩 `30~80` 页

### 2.3 PureDiablo D2Wiki
优先扩：
- 职业技能页
- FAQ / manual 页
- area / mechanic / rune / set / mercenary 页

建议追加量：
- 再扩 `20~60` 页

---

## P1：结构化增强（和抓取并行）

## 3. Build / FAQ / Route 结构化

不是只抓正文，而是要从现有正文中继续抽：

- build_summary
- skill_plan
- gear_plan
- merc_plan
- route_plan
- faq_pairs

为什么：
- 这是当前问答质量最大的缺口之一

---

## 4. 关系增强

优先抽这些关系：

- `USES_RUNE`
- `REQUIRES_BASE`
- `DROPS_IN`
- `BELONGS_TO_CLASS`
- `USED_BY_BUILD`
- `OVERRIDES_IN_PATCH`

为什么：
- 这是 GraphRAG 从“能查”变成“能推”的关键

---

## P2：版本和冲突增强

## 5. 版本差异资料

需要补：
- LoD / D2R patch notes
- 版本差异 FAQ
- 旧版与 D2R 差异页

为什么：
- 版本问答当前仍不够稳定

---

## P3：低优先但有价值

## 6. 社区精华帖

适合补：
- CNBN / 社区精华
- 中文 build / FAQ 长帖
- 历史经验帖

但规则必须严格：
- 只抓长文 / 置顶 / FAQ / 精华
- 不抓交易 / 估价 / 灌水

---

## 推荐执行顺序

如果下一轮只做 4 件事，建议：

1. 扩 91D2
2. 扩 TTBN
3. 扩 diablo2.io / Arreat / PureDiablo 深页
4. 同步做 build / FAQ / route 结构化抽取

---

## 成功标准

下一阶段至少达到：

- 中文高质量页总量 > `150`
- high-value chunks 总量 > `4000`
- merged chunks 总量 > `10000`
- merged canonical claims > `1000`
- 中文 FAQ / build / 路线问答效果明显提升

