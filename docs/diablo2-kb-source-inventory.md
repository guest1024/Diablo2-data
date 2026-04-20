# Diablo II Knowledge Base — Source Inventory

This inventory is optimized for a later **GraphRAG + Agent** pipeline. It prioritizes **coverage + provenance + structured ingestability** over naive page mirroring.

## Capture Policy Baseline
- Scope: public web + public APIs only
- Versions: Diablo II Classic / LoD 1.13 + Diablo II: Resurrected
- Languages: English + Chinese
- Default keep policy: **structured-first**
- Authority order: **official > structured wiki/db > guides > forum posts**
- Conflict rule: keep conflicting claims as separate sourced facts

## Source Table

| Tier | Source | URL | Lane | Lang | Coverage | Recommended capture mode | Notes / policy signal |
|---|---|---|---|---|---|---|---|
| 0 | The Arreat Summit | https://classic.battle.net/diablo2exp/ | Official | EN | Classic canonical reference: classes, skills, items, monsters, quests, cube, runes | Category crawl + HTML-to-markdown extraction | Highest authority for legacy mechanics |
| 0 | Diablo II CN official portal | https://d2.blizzard.cn/ | Official | ZH | Chinese official naming, news, support-facing terminology | News/support metadata crawl; terminology extraction | `robots.txt` exposed and sitemap listed |
| 0 | diablo2.io reference DB | https://diablo2.io/ | Structured DB | EN | uniques, runewords, sets, base items, recipes, monsters, NPCs, skills, areas, quests | Sitemap/category crawl for DB sections; normalize per entity type | `robots.txt` disallows `/builds`, `/articles`, `/tools`, `/trade`; reference DB sections appear crawlable |
| 0 | blizzhackers/d2data | https://github.com/blizzhackers/d2data | Open Data | EN | raw game-data-style files derived from D2R txt/casc | Clone/download raw files; snapshot versions | Best machine-readable seed corpus |
| 0 | Diablo-2.net API | https://www.diablo-2.net/api/ | API | EN | items, runes, unique-items and related structured lookups | Endpoint inventory + periodic JSON snapshots | Supplemental unofficial API; preserve provenance |
| 1 | PureDiablo D2Wiki | https://www.purediablo.com/d2wiki/ | Wiki | EN | broad wiki coverage across items/skills/areas/mechanics | Sitemap-driven content crawl | `robots.txt` explicitly exposes D2Wiki sitemap index |
| 1 | DiabloWiki / Fandom family | e.g. https://diablo2.diablowiki.net/ , https://diablo.fandom.com/wiki/Category:Diablo_II | Wiki | EN | lore/context/aliases/legacy terms | Gap-fill crawl by namespace/category | Use selectively to fill missing entities and terminology |
| 2 | Maxroll D2 | https://maxroll.gg/d2 | Guides/Meta | EN | guides, tier lists, database, planner, farming routes | Metadata/link inventory by default; permission needed for automated content scraping | `robots.txt`/terms explicitly prohibit automated scraping for AI/RAG use without permission |
| 2 | d2runewizard | https://d2runewizard.com/ | Tools/Reference | EN | calculators, resources, runewords/tools | Manual/headful validation lane first | Observed Cloudflare challenge on automation path |
| 2 | PureDiablo guide articles/forums | https://www.purediablo.com/ | Guides/Forums | EN | guides, forum stickies, community knowledge | Curated article extraction; sticky/index-first forum capture | Avoid broad forum recursion initially |
| 3 | NGA D2R discussions | https://nga.178.com/ or https://bbs.nga.cn/ | Community | ZH | builds, farming routes, patch discussion, slang | Curated sticky/index/topic capture | Validate concrete hubs during execution |
| 3 | 17173 D2R guides | https://diablo2.17173.com/ or site-search-discovered sections | Community/Guides | ZH | Chinese guide content and beginner articles | Guide-hub extraction, metadata-first | Validate exact active sections during execution |
| 3 | 游侠/ali213 D2 guide hub | https://gl.ali213.net/z/1262/ | Community/Guides | ZH | walkthroughs and guide aggregations | Guide-hub extraction + link catalog | Good long-tail supplement |
| 3 | TTBN and other long-lived D2 communities | https://www.ttbn.cn/ | Community | ZH | long-tail community knowledge | Manual validation + curated seed pages | Current crawlability unclear; validate before automation |

## Verified Structural Signals

### 1) diablo2.io
Observed sitemap/category URLs include:
- https://diablo2.io/uniques/
- https://diablo2.io/runewords/
- https://diablo2.io/sets/
- https://diablo2.io/base/
- https://diablo2.io/recipes/
- https://diablo2.io/monsters/
- https://diablo2.io/npcs/
- https://diablo2.io/skills/
- https://diablo2.io/areas/
- https://diablo2.io/quests/

Observed robots restrictions include disallow rules for:
- `/tools/*`
- `/builds/*`
- `/articles/*`
- `/trade/*`
- some account/system paths

**Implication:** use diablo2.io as a **high-priority structured source**, but do not default to automated crawl of build/article/trade/tool sections.

### 2) PureDiablo D2Wiki
Observed `robots.txt` / sitemap entries include:
- https://www.purediablo.com/sitemap_index.xml
- https://www.purediablo.com/d2wiki/sitemap/sitemap-index-d2wiki.xml

**Implication:** strong candidate for sitemap-driven wiki ingestion.

### 3) Maxroll D2
Observed sitemap/category URLs include:
- https://maxroll.gg/d2/category/guides
- https://maxroll.gg/d2/category/tierlists
- https://maxroll.gg/d2/database
- https://maxroll.gg/d2/items/runewords
- https://maxroll.gg/d2/items/runes
- https://maxroll.gg/d2/items/unique-items
- https://maxroll.gg/d2/meta/countess-farming-guide

Observed policy signal in `robots.txt` indicates automated scraping/AI/RAG dataset use is prohibited without permission.

**Implication:** keep Maxroll in the corpus map, but default it to **metadata-only / permission-needed** instead of full automated content crawl.

### 4) Diablo-2.net API
Observed public endpoint examples include:
- https://www.diablo-2.net/api/items
- https://www.diablo-2.net/api/items?item=ColossusSword&class=Barbarian&level=99&output=json
- https://www.diablo-2.net/api/runes?item=ElRune&level=1
- https://www.diablo-2.net/api/unique-items?item=TheGrandFather&base-item=colossus_blade&class=Assassin&level=55&strength=75&dexterity=75&theme=d2r&identified=yes&output=json

**Implication:** useful supplemental structured feed for normalized snapshots, especially for item/rune-style lookups.

### 5) blizzhackers/d2data
Observed README states the repository contains Diablo 2 data files based on D2R txt/casc-derived data.

**Implication:** treat as a machine-readable seed set that can bootstrap entity normalization and schema mapping.

## Recommended First-Batch Priority
1. The Arreat Summit
2. diablo2.io structured categories
3. blizzhackers/d2data
4. Diablo-2.net API
5. PureDiablo D2Wiki
6. d2.blizzard.cn official CN terminology/news
7. Restricted/manual lanes: Maxroll, d2runewizard
8. Chinese long-tail community hubs: NGA / 17173 / ali213 / TTBN

## What to Crawl Broadly vs Narrowly

### Broad / high-confidence crawl lanes
- Arreat Summit category sections
- diablo2.io structured reference categories
- PureDiablo D2Wiki content namespaces
- blizzhackers/d2data repository files
- official CN news/support index pages

### Scoped / metadata-first lanes
- Maxroll
- PureDiablo non-wiki guides
- Chinese guide portals
- forum/community sources

### Manual validation first
- d2runewizard (automation challenge)
- ambiguous community sites without clear sitemap/robots posture
