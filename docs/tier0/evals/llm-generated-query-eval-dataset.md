# 基于 Diablo2 语料生成的 Query Eval Dataset

- generated_at: `2026-04-22T12:54:04.539757+00:00`
- case_count: `25`
- generator_mode: `source_grounded_per_seed`
- note: 每条 query 都由当前配置的大模型生成，但生成时显式提供了仓库内 Diablo2 语料证据，不再使用脱离语料的通用 seed prompting。

## Cases

### route_spirit
- query: `暗黑2里的 Spirit 是什么？`
- case_type: `routing`
- canonical: `Spirit`
- expected_intent: `definition`
- expected_source_id: `diablo2-io`
- expected_title_contains: `Spirit`
- generation_note: `基于证据中明确出现的术语 Spirit，并按要求使用中文定义问法与必含短语“是什么”，避免扩展到制作、底材或刷取。`
- reference_titles: `["Spirit • Diablo 2 Resurrected Runeword • diablo2.io"]`
- reference_keywords: `["Spirit • Diablo 2 Resurrected Runeword • diablo2.io", "spirit t3", "spirit-t3"]`
- source_contexts:
  - role: `primary` | source_id: `diablo2-io` | title: `Spirit • Diablo 2 Resurrected Runeword • diablo2.io`
  - excerpt: `Spirit is an excellent end-game caster shield and mid-game weapon Runeword. It's fairly inexpensive (considering the skill bonus) and is often rolled many times to get 35% Faster Cast Rate. The only drawback is that the shield version requires a base shield with 4 sockets, and th…`

### route_shako
- query: `军帽是啥？`
- case_type: `routing`
- canonical: `Harlequin Crest / 军帽 / Shako`
- expected_intent: `definition`
- expected_source_id: `diablo2-io`
- expected_title_contains: `Harlequin Crest`
- generation_note: `基于证据中的 Harlequin Crest / Shako，生成中文俗称定义问法，包含必需词和必需短语，且避免刷取/配装等意图。`
- reference_titles: `["Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io"]`
- reference_keywords: `["Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io", "harlequin crest t37", "harlequin-crest-t37"]`
- source_contexts:
  - role: `primary` | source_id: `diablo2-io` | title: `Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io`
  - excerpt: `Shako Defense: 98-141 Durability: 12 Req Strength: 50 Req level: 62 Quality level: 69 Treasure class: 60 +2 To All Skills + (1.5 Per Character Level) 1-148 To Life (Based On Character Level) + (1.5 Per Character Level) 1-148 To Mana (Based On Character Level) Damage Reduced By 10…`

### route_torch
- query: `暗黑2里火炬是啥？`
- case_type: `routing`
- canonical: `Hellfire Torch / 地狱火炬 / 火炬`
- expected_intent: `definition`
- expected_source_id: `diablo2-io`
- expected_title_contains: `Hellfire Torch`
- generation_note: `基于证据聚焦 Hellfire Torch / 地狱火炬 的定义型提问，使用玩家常见简称“火炬”，并包含必需短语“是啥”，避免获取流程相关表述。`
- reference_titles: `["Hellfire Torch • Diablo 2 Resurrected Unique Item • diablo2.io"]`
- reference_keywords: `["Hellfire Torch • Diablo 2 Resurrected Unique Item • diablo2.io", "hellfire torch t39", "hellfire-torch-t39"]`
- source_contexts:
  - role: `primary` | source_id: `diablo2-io` | title: `Hellfire Torch • Diablo 2 Resurrected Unique Item • diablo2.io`
  - excerpt: `Hellfire Torch Normal Unique Large Charm Req level: 75 Quality level: 110 5% Chance To Cast level 10 Firestorm On Striking +3 to Random Character Class Skills + 10-20 To All Attributes All Resistances + 10-20 +8 To Light Radius Level 30 Hydra (10 charges) Patch 1.13 Data contribu…`

### route_soj
- query: `乔丹是啥戒指？`
- case_type: `routing`
- canonical: `Stone of Jordan / 乔丹 / SOJ`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Stone of Jordan`
- generation_note: `基于证据中的中文俗称“乔丹”与其为 Unique Ring 的定义型意图，采用玩家常见简称问法，满足 required terms 与 required phrase。`
- reference_titles: `["Stone of Jordan / 乔丹（Curated Anchor Card）"]`
- reference_keywords: `["Stone of Jordan", "乔丹", "SOJ", "Unique Ring", "+1 to All Skills", "Increase Maximum Mana 25%"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Stone of Jordan / 乔丹（Curated Anchor Card）`
  - excerpt: `Stone of Jordan（乔丹 / SOJ）是 Diablo II 中著名的 Unique Ring。常见识别特征：+1 to All Skills、Increase Maximum Mana 25%。Common Chinese nickname: “乔丹”. English canonical term: “Stone of Jordan”. Primary supporting surfaces in current corpus: Diablo2.io uniques listing, Horadric Cube references, a…`

### route_infinity
- query: `暗黑2里无限是啥？`
- case_type: `routing`
- canonical: `Infinity / 无限`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Infinity`
- generation_note: `基于证据中的中文俗称“无限”与英文 canonical term“Infinity”，按定义型单跳问法生成，包含 required term 与 required phrase，且避免扩展到底材/孔数/给谁用等。`
- reference_titles: `["Infinity / 无限（Curated Anchor Card）"]`
- reference_keywords: `["Infinity", "无限", "Runeword", "Ber Mal Ber Ist", "Polearm", "Conviction Aura"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Infinity / 无限（Curated Anchor Card）`
  - excerpt: `Infinity（无限）是 Diablo II 中的高价值 Runeword。常见识别特征：Ber + Mal + Ber + Ist、4 socket Polearm、Level 12 Conviction Aura When Equipped。Common Chinese nickname: “无限”. English canonical term: “Infinity”. Primary supporting surfaces in current corpus: Diablo2.io runewords listing and The Arrea…`

### route_chaos_sanctuary
- query: `超市是啥`
- case_type: `routing`
- canonical: `Chaos Sanctuary / 超市`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Chaos Sanctuary`
- generation_note: `按长度限制生成，使用 required term“超市”和 required phrase“是啥”，保持单跳定义意图。`
- reference_titles: `["Chaos Sanctuary / 超市（Curated Anchor Card）"]`
- reference_keywords: `["Chaos Sanctuary", "超市", "Act IV", "River of Flame", "Diablo"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Chaos Sanctuary / 超市（Curated Anchor Card）`
  - excerpt: `Chaos Sanctuary（超市）= Diablo II Act IV 的关键终局区域。它位于 River of Flame 之后，玩家需要在这里开启五个封印并最终击败 Diablo。Common Chinese community nickname: “超市”. English canonical term: “Chaos Sanctuary”. Primary source in current corpus: The Arreat Summit - Maps: Act IV.`

### route_nova_sorc
- query: `新星电法是什么？`
- case_type: `routing`
- canonical: `Nova Sorceress / 新星电法`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Nova Sorceress`
- generation_note: `基于证据中的中文俗称“新星电法”生成定义型单跳问句，包含 required term 和 required phrase，且避免配装/加点等扩展意图。`
- reference_titles: `["Nova Sorceress / 新星电法（Curated Anchor Card）"]`
- reference_keywords: `["Nova Sorceress", "新星电法", "Sorceress", "Nova", "Lightning"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Nova Sorceress / 新星电法（Curated Anchor Card）`
  - excerpt: `Nova Sorceress（新星电法）= Diablo II 中文社区中对新星流电法玩法的常见称呼。Common Chinese nickname: “新星电法”. English canonical term: “Nova Sorceress”. Primary supporting sources in current corpus include lightning sorceress references.`

### route_countess
- query: `暗黑2里女伯爵是什么怪？`
- case_type: `routing`
- canonical: `The Countess / 女伯爵`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `The Countess`
- generation_note: `基于证据中的 canonical 名称“女伯爵 / The Countess”生成中文定义型单跳问句，包含 required term“女伯爵”和 required phrase“是什么”，避免了刷点、掉落、路线等偏移意图。`
- reference_titles: `["The Countess / 女伯爵（Curated Anchor Card）"]`
- reference_keywords: `["The Countess", "女伯爵", "Act I", "Tower Cellar Level 5"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `The Countess / 女伯爵（Curated Anchor Card）`
  - excerpt: `The Countess（女伯爵）= Diablo II Act I 的 Superunique，典型位置是 Tower Cellar Level 5。Common Chinese nickname: “女伯爵”. English canonical term: “The Countess”. Primary supporting sources in current corpus include Diablo2.io monster listings and Act I references.`

### route_hoto
- query: `HOTO 是什么？`
- case_type: `routing`
- canonical: `Heart of the Oak / HOTO / 橡树之心`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Heart of the Oak`
- generation_note: `基于证据中的简称 HOTO，按中文简称定义问法生成，满足 required phrase，且未扩展到用途、底材或配装。`
- reference_titles: `["Heart of the Oak / HOTO（Curated Anchor Card）"]`
- reference_keywords: `["Heart of the Oak", "HOTO", "橡树之心", "Runeword"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Heart of the Oak / HOTO（Curated Anchor Card）`
  - excerpt: `Heart of the Oak（HOTO / 橡树之心）= Diablo II 中高频使用的 caster Runeword 之一。Common abbreviation: “HOTO”. English canonical term: “Heart of the Oak”. Primary supporting sources in current corpus include rune-word references.`

### route_cta
- query: `CTA 是什么？`
- case_type: `routing`
- canonical: `Call to Arms / 战争召唤 / CTA`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Call to Arms`
- generation_note: `使用证据中的简称 CTA，按中文简称定义问法生成单跳定义类问题，并包含必需短语“是什么”，避免涉及用途、底材、孔数等扩展意图。`
- reference_titles: `["Call to Arms / 战争召唤（Curated Anchor Card）"]`
- reference_keywords: `["Call to Arms", "战争召唤", "CTA", "Runeword", "Battle Orders"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Call to Arms / 战争召唤（Curated Anchor Card）`
  - excerpt: `Call to Arms（战争召唤 / CTA）= Diablo II 中常见的辅助型 Runeword，以提供 Battle Orders 等技能而著名。Common Chinese nickname: “战争召唤”. English canonical term: “Call to Arms”. Primary supporting sources in current corpus include Diablo2.io runewords and The Arreat Summit rune-word references.`

### route_mephisto
- query: `劳模是啥？`
- case_type: `routing`
- canonical: `Mephisto / 劳模`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Mephisto`
- generation_note: `使用证据中的中文社区俗称“劳模”，按定义型路由意图构造单跳问句，并包含 required phrase“是啥”，避开刷点、掉落、路线等词。`
- reference_titles: `["Mephisto / 劳模（Curated Anchor Card）"]`
- reference_keywords: `["Mephisto", "劳模", "Act 3 Boss", "Durance of Hate Level 3"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Mephisto / 劳模（Curated Anchor Card）`
  - excerpt: `Mephisto（劳模）= Diablo II Act III 的 Boss，位置通常在 Durance of Hate Level 3。Common Chinese community nickname: “劳模”. English canonical term: “Mephisto”. Primary supporting sources in current corpus include Diablo2.io monster listings and The Arreat Summit boss pages.`

### route_cow_level
- query: `牛场是啥？`
- case_type: `routing`
- canonical: `Secret Cow Level / 牛场`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Secret Cow Level`
- generation_note: `基于证据中的中文俗称“牛场”与定义型 intent 生成；满足 required_query_terms_any 和 required_phrase_any，且避开了开门、刷图用途等扩展。`
- reference_titles: `["Secret Cow Level / 牛场（Curated Anchor Card）"]`
- reference_keywords: `["Secret Cow Level", "牛场", "Cow Level", "Hell Bovine"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Secret Cow Level / 牛场（Curated Anchor Card）`
  - excerpt: `Secret Cow Level（牛场）= Diablo II 中著名的隐藏区域，常用于刷怪、刷底材和刷符文。Common Chinese nickname: “牛场”. English canonical term: “Secret Cow Level”. Primary supporting source in current corpus: Arreat Summit cow-level materials and related portal recipe references.`

### route_ancient_tunnels
- query: `古代通道是什么？`
- case_type: `routing`
- canonical: `Ancient Tunnels / 古代通道`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Ancient Tunnels`
- generation_note: `基于证据聚焦 Ancient Tunnels / 古代通道 的区域定义问法，满足 required term 与 required phrase，避免路线、入口、刷图等偏移意图。`
- reference_titles: `["Ancient Tunnels / 古代通道（Curated Anchor Card）"]`
- reference_keywords: `["Ancient Tunnels", "古代通道", "Act II", "Lost City"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Ancient Tunnels / 古代通道（Curated Anchor Card）`
  - excerpt: `Ancient Tunnels（古代通道）= Diablo II Act II Lost City 下方的重要区域，常被作为刷图地点。Common Chinese nickname: “古代通道”. English canonical term: “Ancient Tunnels”. Primary supporting source in current corpus: The Arreat Summit - Maps: Act II.`

### route_andariel_bug
- query: `暗黑2里说的虫子是啥？`
- case_type: `routing`
- canonical: `Andariel Bug / 虫子`
- expected_intent: `definition`
- expected_source_id: `curated-anchor`
- expected_title_contains: `Andariel Bug`
- generation_note: `使用证据中的中文社区黑话“虫子”，按定义型单跳问法生成，并包含 required phrase“是啥”；避开了操作、掉落、任务、安达利尔、刷法等禁词。`
- reference_titles: `["Andariel Bug / 虫子（Curated Anchor Card）"]`
- reference_keywords: `["Andariel Bug", "虫子", "BUG虫子", "Andariel", "Quest Bug"]`
- source_contexts:
  - role: `primary` | source_id: `curated-anchor` | title: `Andariel Bug / 虫子（Curated Anchor Card）`
  - excerpt: `Andariel Bug（虫子 / BUG虫子）= Diablo II 中文社区中常见说法，通常指 Andariel 相关的任务击杀、掉落或 BUG 讨论语境。Common Chinese slang: “虫子”. English canonical term used here: “Andariel Bug”. Primary supporting sources in current corpus include 91D2 guides and related quest discussions.`

### analysis_spirit_shield_base
- query: `精神盾底材一般是不是 Monarach，做 Spirit 盾要几孔？`
- case_type: `analysis`
- canonical: `Spirit Shield / 精神盾`
- expected_intent: `crafting_base`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦 Spirit Shield 的常见底材 Monarch 以及盾牌版需要 4 sockets，构造成玩家会问的底材/几孔分析型单问句。`
- reference_titles: `["Spirit Shield / 精神盾（Curated Anchor Card）", "Spirit • Diablo 2 Resurrected Runeword • diablo2.io"]`
- reference_keywords: `["Spirit Shield", "精神盾", "Spirit", "Monarch", "军团圣盾", "Spirit • Diablo 2 Resurrected Runeword • diablo2.io", "spirit t3", "spirit-t3"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Spirit Shield / 精神盾（Curated Anchor Card）`
  - excerpt: `Spirit Shield（精神盾）= 玩家语境中通常指把 Spirit 符文之语做在盾牌上，最常见搭配是 Monarch（军团圣盾）底材。Common Chinese phrase: “精神盾”. English canonical term: “Spirit Shield”. Primary supporting sources in current corpus include Spirit runeword references and base-item pages.`
  - role: `support` | source_id: `diablo2-io` | title: `Spirit • Diablo 2 Resurrected Runeword • diablo2.io`
  - excerpt: `Spirit is an excellent end-game caster shield and mid-game weapon Runeword. It's fairly inexpensive (considering the skill bonus) and is often rolled many times to get 35% Faster Cast Rate. The only drawback is that the shield version requires a base shield with 4 sockets, and th…`

### analysis_shako_farm
- query: `军帽 Shako 哪里刷？想问 Hell Mephisto 掉落 farm 是否靠谱。`
- case_type: `analysis`
- canonical: `Harlequin Crest / 军帽 / Shako`
- expected_intent: `farming`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦 Harlequin Crest/军帽/Shako 的刷取意图，并结合 Mephisto 作为相关 farm spot，使用单条分析型问句含两个相关 facet（哪里刷 + Mephisto 掉落 farm）。`
- reference_titles: `["Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io", "All Diablo 2 Resurrected Monsters • diablo2.io"]`
- reference_keywords: `["Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io", "harlequin crest t37", "harlequin-crest-t37", "All Diablo 2 Resurrected Monsters • diablo2.io"]`
- source_contexts:
  - role: `support` | source_id: `diablo2-io` | title: `Harlequin Crest • Diablo 2 Resurrected Unique Item • diablo2.io`
  - excerpt: `HerpaDerpaLiciousMan 4 years ago (pre-Resurrected) https://diablo2.io/post10499.html?sid=52065ba179c99a9755c1fd2a5332f36c#p10499 4 years ago (pre-Resurrected) https://diablo2.io/post10499.html?sid=52065ba179c99a9755c1fd2a5332f36c#p10499 Some potential spots to farm for Harlequin …`
  - role: `support` | source_id: `diablo2-io` | title: `All Diablo 2 Resurrected Monsters • diablo2.io`
  - excerpt: `Mephisto Act 3 Demon Boss Lightning Charged Bolt Blizzard Frost Nova Poison Nova Skull Missile Found in: Durance of Hate Level 3 Stats (Hell): Monster level: 87 Treasure class: 78 Experience: 1148886 Views: 39190 Likes: 0 Comments: 13 Last post: Knappogue , 1 month ago 1771862894…`

### analysis_chaos_path
- query: `从 River of Flame 进超市怎么走，Chaos Sanctuary 里面五个封印的路线一般怎么跑？`
- case_type: `analysis`
- canonical: `Chaos Sanctuary / 超市`
- expected_intent: `location`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦从 River of Flame 进入 Chaos Sanctuary，以及内部五个封印路线；包含必需词与短语，未引入掉落/配装/build等无关内容。`
- reference_titles: `["Chaos Sanctuary / 超市（Curated Anchor Card）", "All Diablo 2 Resurrected Areas • diablo2.io"]`
- reference_keywords: `["Chaos Sanctuary", "超市", "Act IV", "River of Flame", "Diablo", "All Diablo 2 Resurrected Areas • diablo2.io"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Chaos Sanctuary / 超市（Curated Anchor Card）`
  - excerpt: `Chaos Sanctuary（超市）= Diablo II Act IV 的关键终局区域。它位于 River of Flame 之后，玩家需要在这里开启五个封印并最终击败 Diablo。Common Chinese community nickname: “超市”. English canonical term: “Chaos Sanctuary”. Primary source in current corpus: The Arreat Summit - Maps: Act IV.`
  - role: `support` | source_id: `diablo2-io` | title: `All Diablo 2 Resurrected Areas • diablo2.io`
  - excerpt: `River of Flame Act 4 Open Area Area level Normal : 27 Area level Nightmare : 57 Area level Hell : 85 Has Waypoint: Yes Immunes: Cold Fire Lightning Poison Nophysical Nomagic Can be Terrorized Entered from: City of the Damned Leads to: Chaos Sanctuary Views: 16601 Likes: 1 Comment…`

### analysis_pit_usage
- query: `地穴（The Pit）有啥用，适合拿来做 MF 和刷 85 场景吗？`
- case_type: `analysis`
- canonical: `The Pit / 地穴`
- expected_intent: `usage`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦 The Pit/地穴 的用途与适用场景，结合锚点中的 MF 用途及支持证据里的 Hell 85 区域等级，保持单跳分析型问法。`
- reference_titles: `["The Pit / 地穴（Curated Anchor Card）", "All Diablo 2 Resurrected Areas • diablo2.io"]`
- reference_keywords: `["The Pit", "地穴", "Tamoe Highland", "Act I", "Pit Level 1", "Pit Level 2", "All Diablo 2 Resurrected Areas • diablo2.io"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `The Pit / 地穴（Curated Anchor Card）`
  - excerpt: `The Pit（地穴）= Diablo II Act I Tamoe Highland 下的重要地下区域，通常分为 Pit Level 1 / Level 2，常作为刷图与 MF 路线的一部分。Common Chinese nickname: “地穴”. English canonical term: “The Pit”. Primary supporting sources in current corpus include area and map pages.`
  - role: `support` | source_id: `diablo2-io` | title: `All Diablo 2 Resurrected Areas • diablo2.io`
  - excerpt: `Pit Level 1 Act 1 Underground Area Area level Normal : 7 Area level Nightmare : 39 Area level Hell : 85 Immunes: Cold Fire Lightning Poison Nophysical Nomagic Can be Terrorized Entered from: Tamoe Highland Leads to: Pit Level 2 Views: 22887 Likes: 0 Comments: 2 Last post: Deleted…`

### analysis_infinity_base
- query: `无限底材用几孔 Polearm，Scythe 能不能做？`
- case_type: `analysis`
- canonical: `Infinity / 无限`
- expected_intent: `crafting_base`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `围绕 Infinity / 无限 的符文之语底材与孔数提问，结合证据中的 4 socket Polearm 与 Scythe 线索，保持单条分析型问法且避开掉落/刷取/区别取舍等禁词。`
- reference_titles: `["Infinity / 无限（Curated Anchor Card）", "Scythe • Diablo 2 Resurrected Base Item • diablo2.io"]`
- reference_keywords: `["Infinity", "无限", "Runeword", "Ber Mal Ber Ist", "Polearm", "Conviction Aura", "Scythe • Diablo 2 Resurrected Base Item • diablo2.io", "scythe t61", "scythe-t61"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Infinity / 无限（Curated Anchor Card）`
  - excerpt: `Infinity（无限）是 Diablo II 中的高价值 Runeword。常见识别特征：Ber + Mal + Ber + Ist、4 socket Polearm、Level 12 Conviction Aura When Equipped。Common Chinese nickname: “无限”. English canonical term: “Infinity”. Primary supporting surfaces in current corpus: Diablo2.io runewords listing and The Arrea…`
  - role: `support` | source_id: `diablo2-io` | title: `Scythe • Diablo 2 Resurrected Base Item • diablo2.io`
  - excerpt: `…o2.io/post3992179.html?sid=1c603b66bd5f2414d6e645cbdeb00ae2#p3992179 Popular choice for a self-wielding Infinity Nova Sorceress. 0 8 Similar pages War Scythe Last post by Teebling « 4 years ago Posted in Base by Teebling » 4 years ago » in Base 0 Replies 27728 Views Last post by …`

### analysis_nova_build
- query: `新星电法配装怎么玩，ES 用 Memory 预buff、自持 Infinity Scythe 这套练法怎么搭？`
- case_type: `analysis`
- canonical: `Nova Sorceress / 新星电法`
- expected_intent: `build`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据生成，围绕 Nova Sorceress 的练法/配装，包含 ES、Memory、Scythe 线索；单条 analysis 风格问题，未引入额外物品或比较意图。`
- reference_titles: `["Nova Sorceress / 新星电法（Curated Anchor Card）", "Memory • Diablo 2 Resurrected Runeword • diablo2.io", "Scythe • Diablo 2 Resurrected Base Item • diablo2.io"]`
- reference_keywords: `["Nova Sorceress", "新星电法", "Sorceress", "Nova", "Lightning", "Memory • Diablo 2 Resurrected Runeword • diablo2.io", "memory t1191", "memory-t1191", "Scythe • Diablo 2 Resurrected Base Item • diablo2.io", "scythe t61", "scythe-t61"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Nova Sorceress / 新星电法（Curated Anchor Card）`
  - excerpt: `Nova Sorceress（新星电法）= Diablo II 中文社区中对新星流电法玩法的常见称呼。Common Chinese nickname: “新星电法”. English canonical term: “Nova Sorceress”. Primary supporting sources in current corpus include lightning sorceress references.`
  - role: `support` | source_id: `diablo2-io` | title: `Memory • Diablo 2 Resurrected Runeword • diablo2.io`
  - excerpt: `4 socket Staves +3 to Sorceress Skill Levels 33% Faster Cast Rate Increase Maximum Mana 20% +3 Energy Shield (Sorceress Only) +2 Static Field (Sorceress Only) +10 To Energy +10 To Vitality +9 To Minimum Damage -25% Target Defense Magic Damage Reduced By 7 +50% Enhanced Defense Da…`
  - role: `support` | source_id: `diablo2-io` | title: `Scythe • Diablo 2 Resurrected Base Item • diablo2.io`
  - excerpt: `…179.html?sid=1c603b66bd5f2414d6e645cbdeb00ae2#p3992179 Popular choice for a self-wielding Infinity Nova Sorceress. 0 8 Similar pages War Scythe Last post by Teebling « 4 years ago Posted in Base by Teebling » 4 years ago » in Base 0 Replies 27728 Views Last post by Teebling 4 yea…`

### analysis_hoto_usage
- query: `HOTO 有啥用，适合哪些 caster 职业？`
- case_type: `analysis`
- canonical: `Heart of the Oak / HOTO / 橡树之心`
- expected_intent: `usage`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据中明确出现的 HOTO/Heart of the Oak/橡树之心 与 caster 关联，生成围绕用途与适用职业的单跳 analysis 问句；包含 required term“HOTO”和 required phrase“有啥用”，且避开定义、底材、孔数、刷取、配装等意图。`
- reference_titles: `["Heart of the Oak / HOTO（Curated Anchor Card）", "All Diablo 2 Resurrected Runewords • diablo2.io"]`
- reference_keywords: `["Heart of the Oak", "HOTO", "橡树之心", "Runeword", "All Diablo 2 Resurrected Runewords • diablo2.io"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Heart of the Oak / HOTO（Curated Anchor Card）`
  - excerpt: `Heart of the Oak（HOTO / 橡树之心）= Diablo II 中高频使用的 caster Runeword 之一。Common abbreviation: “HOTO”. English canonical term: “Heart of the Oak”. Primary supporting sources in current corpus include rune-word references.`
  - role: `support` | source_id: `diablo2-io` | title: `All Diablo 2 Resurrected Runewords • diablo2.io`
  - excerpt: `… Last post: Trang Oul , 11 months ago 1746522419 Weapons Missing v0.3 Data Venom Original Runeword Tal Dol Mal Req level: 49 3 socket All Weapons Weapons Hit Causes Monster To Flee 25% Prevent Monster Heal Ignore Target's Defense 7% Mana Stolen Per Hit Level 15 Poison Explosion (…`

### analysis_cta_usage
- query: `CTA 有啥用，除了 BO 以外适合拿来做辅助吗？`
- case_type: `analysis`
- canonical: `Call to Arms / 战争召唤 / CTA`
- expected_intent: `usage`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据中的 Call to Arms/战争召唤/CTA 以及其提供 Battle Orders、Battle Command、Battle Cry 等辅助技能，构造用途/适用场景型分析问句，包含 required term 与 required phrase，且避开定义、底材、孔数、刷取、配装等意图。`
- reference_titles: `["Call to Arms / 战争召唤（Curated Anchor Card）", "The Arreat Summit - Items: Rune Words: 1.10 Rune Words"]`
- reference_keywords: `["Call to Arms", "战争召唤", "CTA", "Runeword", "Battle Orders", "The Arreat Summit - Items: Rune Words: 1.10 Rune Words", "runewords 110", "runewords-110"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Call to Arms / 战争召唤（Curated Anchor Card）`
  - excerpt: `Call to Arms（战争召唤 / CTA）= Diablo II 中常见的辅助型 Runeword，以提供 Battle Orders 等技能而著名。Common Chinese nickname: “战争召唤”. English canonical term: “Call to Arms”. Primary supporting sources in current corpus include Diablo2.io runewords and The Arreat Summit rune-word references.`
  - role: `support` | source_id: `arreat-summit` | title: `The Arreat Summit - Items: Rune Words: 1.10 Rune Words`
  - excerpt: `Call To Arms* 5 Socket Weapons Amn + Ral + Mal + Ist + Ohm +1 To All Skills +40% Increased Attack Speed +250-290% Enhanced Damage (varies) Adds 5-30 Fire Damage 7% Life Stolen Per Hit +2-6 To Battle Command (varies)* +1-6 To Battle Orders (varies)* +1-4 To Battle Cry (varies)* Pr…`

### analysis_mephisto_farm
- query: `劳模在 Durance of Hate Level 3 farm 的话主要掉落怎么样，Hell 难度的 treasure class 值不值得刷？`
- case_type: `analysis`
- canonical: `Mephisto / 劳模`
- expected_intent: `farming`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦 Mephisto/劳模 的刷取与掉落分析，包含 required term“劳模”“Durance of Hate Level 3”以及 required phrase“farm”“掉落”，且避免路线/定义/配装等偏题表达。`
- reference_titles: `["Mephisto / 劳模（Curated Anchor Card）", "All Diablo 2 Resurrected Monsters • diablo2.io"]`
- reference_keywords: `["Mephisto", "劳模", "Act 3 Boss", "Durance of Hate Level 3", "All Diablo 2 Resurrected Monsters • diablo2.io"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Mephisto / 劳模（Curated Anchor Card）`
  - excerpt: `Mephisto（劳模）= Diablo II Act III 的 Boss，位置通常在 Durance of Hate Level 3。Common Chinese community nickname: “劳模”. English canonical term: “Mephisto”. Primary supporting sources in current corpus include Diablo2.io monster listings and The Arreat Summit boss pages.`
  - role: `support` | source_id: `diablo2-io` | title: `All Diablo 2 Resurrected Monsters • diablo2.io`
  - excerpt: `Mephisto Act 3 Demon Boss Lightning Charged Bolt Blizzard Frost Nova Poison Nova Skull Missile Found in: Durance of Hate Level 3 Stats (Hell): Monster level: 87 Treasure class: 78 Experience: 1148886 Views: 39190 Likes: 0 Comments: 13 Last post: Knappogue , 1 month ago 1771862894…`

### analysis_ancient_tunnels_location
- query: `A2 Lost City 的古代通道入口在哪里，怎么走？`
- case_type: `analysis`
- canonical: `Ancient Tunnels / 古代通道`
- expected_intent: `location`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `基于证据聚焦 Ancient Tunnels 位于 Act II 的 Lost City，并按位置/入口意图构造单跳分析型问句，包含 required term 与 required phrase。`
- reference_titles: `["Ancient Tunnels / 古代通道（Curated Anchor Card）", "The Arreat Summit - Maps: Act II"]`
- reference_keywords: `["Ancient Tunnels", "古代通道", "Act II", "Lost City", "The Arreat Summit - Maps: Act II", "act2"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Ancient Tunnels / 古代通道（Curated Anchor Card）`
  - excerpt: `Ancient Tunnels（古代通道）= Diablo II Act II Lost City 下方的重要区域，常被作为刷图地点。Common Chinese nickname: “古代通道”. English canonical term: “Ancient Tunnels”. Primary supporting source in current corpus: The Arreat Summit - Maps: Act II.`
  - role: `support` | source_id: `arreat-summit` | title: `The Arreat Summit - Maps: Act II`
  - excerpt: `Lost City Levels: N/A Quest Related Areas/Monsters: None Waypoint: Yes Caves/Additional Zones: Ancient Tunnels (1 Level) Valley of Snakes Levels: N/A Quest Related Areas/Monsters: Claw Viper Temple Waypoint: No Caves/Additional Zones: Claw Viper Temple (2 Levels) Lut Gholein Leve…`

### analysis_cow_usage
- query: `牛场有啥用，适合刷底材和刷符文吗？`
- case_type: `analysis`
- canonical: `Secret Cow Level / 牛场`
- expected_intent: `usage`
- expected_source_id: `None`
- expected_title_contains: `None`
- generation_note: `围绕牛场用途，结合证据中的刷底材/刷符文两个相关 facet，保持单跳分析型问法。`
- reference_titles: `["Secret Cow Level / 牛场（Curated Anchor Card）", "The Arreat Summit - The Secret Cow Level"]`
- reference_keywords: `["Secret Cow Level", "牛场", "Cow Level", "Hell Bovine", "The Arreat Summit - The Secret Cow Level", "cow"]`
- source_contexts:
  - role: `anchor` | source_id: `curated-anchor` | title: `Secret Cow Level / 牛场（Curated Anchor Card）`
  - excerpt: `Secret Cow Level（牛场）= Diablo II 中著名的隐藏区域，常用于刷怪、刷底材和刷符文。Common Chinese nickname: “牛场”. English canonical term: “Secret Cow Level”. Primary supporting source in current corpus: Arreat Summit cow-level materials and related portal recipe references.`
  - role: `support` | source_id: `arreat-summit` | title: `The Arreat Summit - The Secret Cow Level`
  - excerpt: `The leader of the Cows is the Cow King. He is a Lightning Enchanted, SuperUnique Hell Bovine. If you can kill him, he may drop something special. The Cow King can be difficult to recognize because of his similar appearance to the other cows. You will know you have found him when …`

