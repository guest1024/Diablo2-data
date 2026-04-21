# Manual Gap Check — 2026-04-21

本轮针对第一版系统做了人工查询核验，目标是确认：

1. 核心 required query 是否稳定
2. 第二批中文黑话 / 俗称 query 当前到什么程度

---

## 已验证稳定的核心问法

基于 `python scripts/smoke_test_first_system.py` 的最新输出：

- `Spirit 是什么？`
  - top chunk: `Spirit • Diablo 2 Resurrected Runeword • diablo2.io`
  - source: `entity_link`
- `军帽是什么？`
  - top chunk: `Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io`
  - source: `entity_link`
- `精神符文之语是什么？`
  - top chunk: `Spirit • Diablo 2 Resurrected Runeword • diablo2.io`
  - source: `entity_link`
- `What is Hellfire Torch?`
  - top chunk: `Hellfire Torch • Diablo 2 Resurrected Unique Item • diablo2.io`
  - source: `entity_link`

结论：

- 第一版底座对核心实体问法已可稳定命中 canonical 结果

---

## 第二批中文黑话 / 俗称人工检查

以下结果来自本轮交互式核验：

### 1. `古代通道是什么？`

- query expansion 已扩到：
  - `ancient tunnels`
  - `ancient tunnel`
  - `act 2 area`
  - `lost city cave`
- 当前首条有效证据已能命中：
  - `The Arreat Summit - Maps: Act II`
  - 片段中明确包含 `Ancient Tunnels (1 Level)`

状态：**可用，但还不是 canonical area card**

### 2. `劳模是什么？`

- query expansion 已扩到：
  - `mephisto`
  - `hell mephisto`
  - `act 3 demon boss`
  - `durance of hate level 3`
- 当前首条有效证据已能命中：
  - `All Diablo 2 Resurrected Monsters`
  - 片段中明确包含 `Mephisto / Act 3 Demon Boss / Durance of Hate Level 3`

状态：**可用**

### 3. `女伯爵是什么？`

- query expansion 已扩到：
  - `the countess`
  - `countess`
  - `act 1 demon superunique`
  - `tower cellar level 5`
- 当前首条有效证据已命中：
  - `All Diablo 2 Resurrected Monsters`
  - `Tower Cellar Level 5`

状态：**可用**

### 4. `大菠萝是什么？`

- query expansion 已扩到：
  - `diablo`
  - `diablo boss`
  - `act 4 demon boss`
  - `lord of terror`
  - `chaos sanctuary boss`
- 当前首条有效证据可命中：
  - `Act IV - Diablo 2 Wiki`
  - 或 `All Diablo 2 Resurrected Monsters` 中的 Diablo 相关片段

状态：**基本可用，但排序仍可继续优化**

### 5. `超市是什么？`

- query expansion 已扩到：
  - `chaos sanctuary`
  - `river of flame to chaos sanctuary`
  - `chaos sanctuary boss area`
- 最新核验中，当前首结果已经直达：
  - `Chaos Sanctuary / 超市（Curated Anchor Card）`
- 后续候选仍保留：
  - `All Diablo 2 Resurrected Areas`
  - `The Arreat Summit - Maps: Act IV`

状态：**已可稳定直达**

### 6. `乔丹是什么？`

- query expansion 已扩到：
  - `stone of jordan`
  - `the stone of jordan unique ring`
  - `soj`
  - `unique ring +1 to all skills`
  - `increase maximum mana 25`
- 最新核验中，当前首结果已经直达：
  - `Stone of Jordan / 乔丹（Curated Anchor Card）`
- 后续候选仍保留：
  - `All Diablo 2 Resurrected Uniques`
  - 相关 ring / cube / unique 资料页
- 且 `91D2` 的中文统计页已被明显压后

状态：**已可稳定直达**

### 7. `无限是什么？`

- query expansion 已扩到：
  - `infinity`
  - `infinity runeword`
  - `polearm runeword`
  - `level 12 conviction aura`
  - `ber mal ber ist`
- 最新核验中，当前首结果已经直达：
  - `Infinity / 无限（Curated Anchor Card）`
- 后续候选仍保留：
  - `All Diablo 2 Resurrected Runewords`
  - `The Arreat Summit - Items: Rune Words: 1.10 Rune Words`

状态：**已可稳定直达**

---

## 当前阶段结论

### 已经做对的

- 核心中英实体问法已经稳定
- 中文黑话已能通过 bilingual term map 做有效 query expansion
- 第二批俗称中，`古代通道 / 劳模 / 女伯爵 / 大菠萝` 已明显改善

### 还需要继续打磨的

本轮新增本地 curated anchor cards 后：

- `超市`
- `乔丹`
- `无限`
- `劳模`
- `女伯爵`
- `古代通道`
- `牛场`
- `大菠萝`
- `眼光`
- `悔恨`
- `刚毅`
- `战争召唤`
- `地穴`
- `军团圣盾`
- `精神盾`
- `虫子`
- `SOJ`
- `CTA`
- `毁灭`
- `USC`
- `MF`
- `刷宝`
- `DClone`
- `暗黑克隆`
- `巴尔`
- `安达利尔`
- `HOTO`
- `BOTD`
- `COH`
- `马拉`
- `眼球`

都已经能稳定直达本地标准化锚点卡，同时保留原始英文资料页作为后续候选证据。

下一阶段应优先做：

1. bilingual term map 扩表
2. canonical entity bias / rerank
3. 多语言 embedding 替换当前 baseline
