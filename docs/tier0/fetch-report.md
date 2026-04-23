# Tier 0 Acquisition Execution Report

- Generated at: `2026-04-23T09:47:58+00:00`
- Registry: `docs/tier0/source-registry.json`
- Raw root: `docs/tier0/raw`

## Summary

| Source | Captures | Notes |
| --- | ---: | --- |
| The Arreat Summit | 8 | Core section pages + discovered internal URL inventory |
| diablo2.io structured reference | 11 | Sitemap + structured category roots only |
| blizzhackers/d2data | 4 | GitHub README + contents API for root/json/txt |
| Diablo-2.net API | 4 | Docs page + sample endpoint responses |
| Diablo II China official portal | 3 | Homepage + sitemap + news index |

## Capture Details

### The Arreat Summit

- Tier: `0`
- Lane: `official`
- Capture mode: `scoped`
- Policy note: Legacy official site; no robots.txt was found during planning, so execution is limited to core section pages and discovered internal inventories.

- `homepage` → `cached (200)` → `docs/tier0/raw/arreat-summit/homepage.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `basics` → `cached (200)` → `docs/tier0/raw/arreat-summit/basics.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `classes` → `cached (200)` → `docs/tier0/raw/arreat-summit/classes.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `skills` → `cached (200)` → `docs/tier0/raw/arreat-summit/skills.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `items` → `cached (200)` → `docs/tier0/raw/arreat-summit/items.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `monsters` → `cached (200)` → `docs/tier0/raw/arreat-summit/monsters.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `quests` → `cached (200)` → `docs/tier0/raw/arreat-summit/quests.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`
- `maps` → `cached (200)` → `docs/tier0/raw/arreat-summit/maps.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://classic.battle.net/diablo2exp/`, `https://classic.battle.net/diablo2exp/faq/ladder.shtml`, `https://classic.battle.net/diablo2exp/basics/`, `https://classic.battle.net/diablo2exp/classes/`, `https://classic.battle.net/diablo2exp/skills/`

### diablo2.io structured reference

- Tier: `0`
- Lane: `structured_db`
- Capture mode: `scoped`
- Policy note: Fetch sitemap plus allowed structured category roots only. Skip forum/build/article/tool/trade recursion because of robots restrictions and quality policy.

- `sitemap` → `cached (200)` → `docs/tier0/raw/diablo2-io/sitemap.xml`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/uniques/`, `https://diablo2.io/runewords/`, `https://diablo2.io/sets/`, `https://diablo2.io/base/`, `https://diablo2.io/recipes/`
- `uniques` → `cached (200)` → `docs/tier0/raw/diablo2-io/uniques.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/uniques/?sid=ad68fd24e61bfceeedf8eea7e47ef978`, `https://diablo2.io/uniques/hellslayer-t814.html`, `https://diablo2.io/base/decapitator-t1612.html`
- `runewords` → `cached (200)` → `docs/tier0/raw/diablo2-io/runewords.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/runewords/?sid=f1491178124bb86d6e41197935a09bfa`, `https://diablo2.io/runewords/mania-t1674022.html`, `https://diablo2.io/misc/shael-t1319.html`
- `sets` → `cached (200)` → `docs/tier0/raw/diablo2-io/sets.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/sets/?sid=7defa0000f99aeff8740bc20091edc16`, `https://diablo2.io/sets/horazon-s-splendor-t1673911.html`, `https://diablo2.io/sets/horazon-s-countenance-t1673917.html`
- `base` → `cached (200)` → `docs/tier0/raw/diablo2-io/base.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/base/?sid=3c7dd0692527494aa7aed292c8d89e00`, `https://diablo2.io/base/jared-s-stone-t1775.html`, `https://diablo2.io/base/dimensional-shard-t1785.html`
- `recipes` → `cached (200)` → `docs/tier0/raw/diablo2-io/recipes.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/recipes/?sid=8be948ce82484a02f8e4b441c5a98c37`, `https://diablo2.io/recipes/recipe-fully-repaired-armor-t3303.html`, `https://diablo2.io/misc/ral-t48.html`
- `monsters` → `cached (200)` → `docs/tier0/raw/diablo2-io/monsters.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/monsters/?sid=095e6153849afb5df1219ebf9d515a2f`, `https://diablo2.io/monsters/uber-madawc-t1674869.html`, `https://diablo2.io/areas/colossal-summit-t1674854.html`
- `npcs` → `cached (200)` → `docs/tier0/raw/diablo2-io/npcs.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/npcs/?sid=42fb9efa56369ea43219a46f9c85e688`, `https://diablo2.io/npcs/hratli-t3946.html`, `https://diablo2.io/areas/kurast-docks-t3762.html`
- `skills` → `cached (200)` → `docs/tier0/raw/diablo2-io/skills.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/skills/?sid=f71064750da32b6c83841da1c1a65bcb`, `https://diablo2.io/skills/enhanced-entropy-t1676856.html`, `https://diablo2.io/skills/miasma-chain-t1676851.html`
- `areas` → `cached (200)` → `docs/tier0/raw/diablo2-io/areas.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/areas/?sid=fe165d525e23424c2311540a1ad6b504`, `https://diablo2.io/areas/colossal-summit-t1674854.html`, `https://diablo2.io/areas/blood-moor-t3711.html`
- `quests` → `cached (200)` → `docs/tier0/raw/diablo2-io/quests.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://diablo2.io/areas/`, `https://diablo2.io/quests/`, `https://diablo2.io/quests/?sid=78ed2621a99664cedcaf3c26a4ea709b`, `https://diablo2.io/quests/eve-of-destruction-t3988.html`, `https://diablo2.io/quests/the-search-for-cain-t11.html`

### blizzhackers/d2data

- Tier: `0`
- Lane: `open_data`
- Capture mode: `scoped`
- Policy note: Public GitHub repository suitable for machine-readable seeding. Capture README plus API listings for root/json/txt directories.

- `readme` → `cached (200)` → `docs/tier0/raw/blizzhackers-d2data/README.md`
  - Note: reused existing capture and bootstrapped snapshot metadata
- `root-contents` → `cached (200)` → `docs/tier0/raw/blizzhackers-d2data/root-contents.json`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://api.github.com/repos/blizzhackers/d2data/contents/.eslintrc.js?ref=master`, `https://github.com/blizzhackers/d2data/blob/master/.eslintrc.js`, `https://raw.githubusercontent.com/blizzhackers/d2data/master/.eslintrc.js`, `https://api.github.com/repos/blizzhackers/d2data/contents/.gitignore?ref=master`, `https://github.com/blizzhackers/d2data/blob/master/.gitignore`
- `json-contents` → `cached (200)` → `docs/tier0/raw/blizzhackers-d2data/json-contents.json`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://api.github.com/repos/blizzhackers/d2data/contents/json/.gitkeep?ref=master`, `https://github.com/blizzhackers/d2data/blob/master/json/.gitkeep`, `https://raw.githubusercontent.com/blizzhackers/d2data/master/json/.gitkeep`, `https://api.github.com/repos/blizzhackers/d2data/contents/json/actinfo.json?ref=master`, `https://github.com/blizzhackers/d2data/blob/master/json/actinfo.json`
- `txt-contents` → `cached (200)` → `docs/tier0/raw/blizzhackers-d2data/txt-contents.json`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://api.github.com/repos/blizzhackers/d2data/contents/txt/.gitkeep?ref=master`, `https://github.com/blizzhackers/d2data/blob/master/txt/.gitkeep`, `https://raw.githubusercontent.com/blizzhackers/d2data/master/txt/.gitkeep`, `https://api.github.com/repos/blizzhackers/d2data/contents/txt/base?ref=master`, `https://github.com/blizzhackers/d2data/tree/master/txt/base`

### Diablo-2.net API

- Tier: `0`
- Lane: `api`
- Capture mode: `scoped`
- Policy note: Capture API docs and public error/guard behavior. Current live endpoint responses indicate an API key is required for live rune/unique queries.

- `api-docs` → `cached (200)` → `docs/tier0/raw/diablo2-net-api/api-docs.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://www.diablo-2.net/api/`, `https://www.diablo-2.net/api/items-list`, `https://www.diablo-2.net/api/runes-list`, `https://www.diablo-2.net/api/example.html`
- `items-endpoint` → `cached (200)` → `docs/tier0/raw/diablo2-net-api/items-endpoint.json`
  - Note: reused existing capture and bootstrapped snapshot metadata
- `runes-endpoint` → `cached (200)` → `docs/tier0/raw/diablo2-net-api/runes-endpoint.json`
  - Note: reused existing capture and bootstrapped snapshot metadata
- `unique-items-endpoint` → `cached (200)` → `docs/tier0/raw/diablo2-net-api/unique-items-endpoint.json`
  - Note: reused existing capture and bootstrapped snapshot metadata

### Diablo II China official portal

- Tier: `0`
- Lane: `official`
- Capture mode: `scoped`
- Policy note: Capture homepage, sitemap, and news index to seed official Chinese terminology/news references.

- `homepage` → `cached (200)` → `docs/tier0/raw/blizzard-cn-d2/homepage.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
- `sitemap` → `cached (200)` → `docs/tier0/raw/blizzard-cn-d2/sitemap.txt`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://d2.blizzard.cn/index.html`, `https://d2.blizzard.cn/news/`, `https://d2.blizzard.cn/news/20260203/42929_1285202.html`, `https://d2.blizzard.cn/news/24271875/index.html`, `https://d2.blizzard.cn/news/262126142/index.html`
- `news-index` → `cached (200)` → `docs/tier0/raw/blizzard-cn-d2/news-index.html`
  - Note: reused existing capture and bootstrapped snapshot metadata
  - Discovered URLs sample: `https://d2.blizzard.cn/news/24271875/index.html`, `https://d2.blizzard.cn/news/262126142/index.html`, `https://d2.blizzard.cn/news/24243863/index.html`, `https://d2.blizzard.cn/news/24246296/index.html`, `https://d2.blizzard.cn/news/20260203/42929_1285202.html`

## Tier 0 Execution Notes

- `The Arreat Summit`: fetched core section pages for official legacy reference coverage.
- `diablo2.io`: fetched sitemap plus allowed structured category roots only; avoided forum/build/article/tool/trade expansion.
- `blizzhackers/d2data`: fetched public GitHub API listings plus README/raw samples to seed machine-readable ingestion.
- `Diablo-2.net API`: captured the API docs page and current public error/guard behavior; live JSON item/rune endpoints now appear to require an API key.
- `d2.blizzard.cn`: captured homepage, sitemap, and news index for official Chinese terminology/news seeding.
