# Diablo II Knowledge Base — Phase 1 Execution Plan

## Phase 1 Deliverable
Produce an execution-ready source map and ingestion design for a broad Diablo II corpus, then hand off to execution to start harvesting **Tier 0** lanes first.

## Rollout Phases

### Phase A — Registry and policy baseline
- Create canonical source registry from `docs/diablo2-kb-source-inventory.md`
- Assign each source a lane:
  - `official`
  - `structured_db`
  - `wiki`
  - `api`
  - `open_data`
  - `guide`
  - `forum`
- Assign each source a capture mode:
  - `full`
  - `scoped`
  - `metadata_only`
  - `manual_only`

### Phase B — Tier 0 harvesters
Implement first on:
1. Arreat Summit
2. diablo2.io structured reference categories
3. blizzhackers/d2data
4. Diablo-2.net API
5. Blizzard CN official terminology/news

## Tier 0 Execution Matrix

| Source | Discovery seeds | Raw capture artifacts | First normalized outputs | Policy gate / downgrade rule |
|---|---|---|---|---|
| Arreat Summit | category indexes for classes, skills, items, runes/runewords, monsters, areas, quests, Horadric Cube | `raw/html/arreat-summit/...` page snapshots + `raw/indexes/arreat-summit/*.json` seed manifests | `Class`, `Skill`, `Item`, `Rune`, `Runeword`, `Monster`, `Area`, `Quest`, `Recipe` entities + sourced claims | If sections add anti-bot friction or robots restrictions change, downgrade to seed-manifest + manual queue until reviewed |
| diablo2.io reference DB | `/uniques/`, `/runewords/`, `/sets/`, `/base/`, `/recipes/`, `/monsters/`, `/npcs/`, `/skills/`, `/areas/`, `/quests/` | `raw/html/diablo2-io/...` entity pages + `raw/indexes/diablo2-io/*.json` category enumerations | `UniqueItem`, `SetItem`, `BaseItem`, `Recipe`, `Monster`, `NPC`, `Skill`, `Area`, `Quest` entities + alias links | Never crawl `/builds`, `/articles`, `/tools`, `/trade`; if an entity path resolves into those sections, record metadata only |
| blizzhackers/d2data | repository root + structured data directories at a pinned commit | `raw/files/blizzhackers-d2data/<commit>/...` + commit manifest | open-data file records, schema maps, extracted canonical IDs, alias seeds | If source layout changes or repo becomes unavailable, pin last reachable commit and mark freshness gap instead of improvising alternate mirrors |
| Diablo-2.net API | `/api/items`, `/api/runes`, `/api/unique-items` plus response-shape inventory | `raw/json/diablo-2-net/<endpoint>/...` snapshots + endpoint catalog | item/rune/unique-item records with request params, response schema, provenance metadata | If rate limits or anti-abuse controls appear, switch to sampled endpoint snapshots and record missing coverage explicitly |
| Blizzard CN official portal | news/support sections, terminology pages, sitemap/robots references | `raw/html/d2-blizzard-cn/...` pages + `raw/indexes/d2-blizzard-cn/*.json` URL inventories | localized aliases, official Chinese terms, news/support metadata docs | Keep capture scoped to public news/support/terminology pages; if auth or dynamic-only rendering is required, downgrade to metadata-only |

### Phase C — Tier 1 expansion
- PureDiablo D2Wiki
- supplementary wiki families for gap filling
- CN official/news archive expansion

### Phase D — Restricted/manual lanes
- Maxroll metadata registry and permission review
- d2runewizard manual validation
- Chinese guide hubs and curated forum seeds

## First-Batch Priority Order

### Batch 1 — Highest value / lowest ambiguity
- Arreat Summit
- blizzhackers/d2data
- diablo2.io structured categories
- Diablo-2.net API

### Batch 2 — Strong coverage expansion
- PureDiablo D2Wiki
- d2.blizzard.cn news/terminology

### Batch 3 — Controlled long-tail expansion
- Maxroll metadata inventory only
- CN guide/community hubs
- curated forum stickies and FAQ collections

## Stop / Quality Gates
Do not widen to the next batch until:
1. seed URLs and category lists are stable
2. source policy mode is recorded
3. raw → normalized → derived mapping is defined for the lane
4. at least one representative entity family was successfully modeled
5. provenance fields are preserved end to end

## Batch 1 Verification Checklist

Before moving beyond Batch 1, capture evidence for each Tier 0 source showing:
- a checked-in or archived seed/index manifest for discovery inputs
- at least one representative raw artifact in the expected storage layer (`html`, `json`, or `files`)
- at least one normalized entity or claim record with provenance fields populated
- an explicit capture-mode decision (`full`, `scoped`, `metadata_only`, or `manual_only`)
- any downgrade reason when a site cannot remain on the default automation path

## Policy Downgrade Triggers
- **Robots / ToS conflict:** immediately downgrade to `metadata_only` or `manual_only`; do not continue speculative automation.
- **Anti-bot / Cloudflare challenge:** keep the source in scope, but move it to manual validation unless a clearly compliant path is found.
- **Unstable discovery surface:** if category pages, sitemap entries, or endpoint inventory change during capture, freeze the last verified seed list and note the freshness gap.
- **Schema drift in structured sources:** version the response/file shape and keep old + new mappings side by side until normalization is updated.

## Source-Specific Capture Guidance
- **Arreat Summit:** category pages first, then drill into entity pages
- **diablo2.io:** crawl only allowed reference categories; skip robots-disallowed productized/community sections
- **blizzhackers/d2data:** snapshot raw files by version/commit
- **Diablo-2.net API:** enumerate endpoints and response shapes before scaling calls
- **PureDiablo D2Wiki:** use sitemap-first discovery, then namespace filtering
- **Maxroll:** metadata/link inventory only unless permission is obtained
- **Forums:** sticky/index-first, not breadth-first thread recursion

## What “尽可能全” Means Operationally
It means:
- wide source discovery
- explicit inclusion of both legacy D2 and D2R
- bilingual source coverage
- long-tail community sources tracked in the registry

It does **not** mean:
- automatic permission to mirror every page on every site
- losing provenance during normalization
- mixing contradictory claims into a single flattened record

## Recommended Next Execution Command
- Sequential owner: `$ralph .omx/plans/prd-diablo2-knowledge-base-phase1.md`
- Parallel team: `$team .omx/plans/prd-diablo2-knowledge-base-phase1.md`
