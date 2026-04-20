# Diablo II Knowledge Base — GraphRAG Design

## Goal
Turn multi-source Diablo II knowledge into a **typed, provenance-rich retrieval graph** that supports:
- factual lookup (items, runes, runewords, areas, monsters, cube recipes)
- build/meta retrieval
- patch/version disambiguation
- Chinese/English alias resolution
- source-aware answer synthesis with authority ordering

## Storage Layers

### 1) Raw layer
Keep the nearest-possible capture artifact:
- `raw/html/...` for public pages
- `raw/json/...` for API responses
- `raw/files/...` for GitHub/open-data files
- `raw/indexes/...` for sitemap, category, and seed URL inventories

### 2) Normalized layer
Convert raw captures into typed records:
- `normalized/entities/*.jsonl`
- `normalized/docs/*.jsonl`
- `normalized/claims/*.jsonl`
- `normalized/aliases/*.jsonl`
- `normalized/links/*.jsonl`

### 3) Derived graph layer
Build graph-ready edges and retrieval chunks:
- `derived/chunks/*.jsonl`
- `derived/nodes/*.jsonl`
- `derived/edges/*.jsonl`
- `derived/conflicts/*.jsonl`
- `derived/embeddings-manifest/*.jsonl`

## Required Metadata Fields
Every normalized doc/chunk should carry at least:
- `source_id`
- `source_name`
- `source_url`
- `captured_at`
- `language`
- `game_variant` (`classic`, `lod`, `d2r`, `unknown`)
- `content_type` (`entity_page`, `guide_article`, `forum_post`, `api_record`, `open_data_file`, `news`, etc.)
- `authority_tier` (`official`, `structured_db`, `guide`, `forum`)
- `entity_types`
- `entity_keys`
- `patch_or_version` (when known)
- `title`
- `site_section`
- `crawl_policy_mode` (`full`, `scoped`, `metadata_only`, `manual_only`)

## Entity Types
Recommended graph nodes:
- `Item`
- `BaseItem`
- `UniqueItem`
- `SetItem`
- `Rune`
- `Runeword`
- `Recipe`
- `Class`
- `Skill`
- `Build`
- `Monster`
- `Area`
- `Quest`
- `NPC`
- `Patch`
- `Mechanic`
- `SourceDocument`
- `Site`
- `Alias`

## Edge Types
Recommended edges:
- `USES_RUNE`
- `CREATES_RUNEWORD`
- `UPGRADES_TO`
- `DROPS_IN`
- `FOUND_IN_AREA`
- `USED_BY_BUILD`
- `BELONGS_TO_CLASS`
- `MODIFIES_SKILL`
- `REQUIRES_LEVEL`
- `REQUIRES_BASE`
- `REQUIRES_RECIPE`
- `MENTIONS_ENTITY`
- `ALIASES`
- `CONTRADICTS`
- `SUPPORTED_BY_SOURCE`
- `OVERRIDES_IN_PATCH`

## Chunking Strategy by Source Type

### Structured entity pages (DB/Wiki/API)
Chunk per **entity** rather than per page.
- Example: one `Runeword` chunk, one `UniqueItem` chunk, one `Monster` chunk.
- Also emit separate claim chunks for dense attributes (stats, drop rules, recipe effects).

### Guide articles
Chunk by semantic sections:
- intro/goal
- gearing
- skill allocation
- mercenary
- farming strategy
- matchups / weaknesses

### Forum/community posts
Chunk narrowly:
- sticky summary
- FAQ answer blocks
- quoted tables or reference sections
- keep thread metadata and reply context

### APIs/open data
Chunk by row/record or compact record groups.
- Example: per item, per rune, per monster row.

## Provenance and Conflict Handling
Do **not** force a single truth during ingestion.
Store claims as:
- `subject`
- `predicate`
- `object`
- `source_id`
- `source_url`
- `authority_tier`
- `game_variant`
- `patch_or_version`
- `confidence`

When two sources disagree:
1. create separate claim records
2. add `CONTRADICTS` or `DIFFERS_FROM` edges
3. rank at query time using authority order and version compatibility

## Bilingual / Alias Handling
Maintain explicit alias tables:
- English item/class/skill names
- Chinese official terms
- Chinese community slang / abbreviations
- legacy vs D2R naming differences

Example alias families:
- `The Pit` ↔ `地穴` (if used in CN guides)
- `Terror Zone` ↔ official/localized CN name
- rune abbreviations and shorthand build names

## Suggested Directory Contract

```text
corpus/
  raw/
    html/
    json/
    files/
    indexes/
  normalized/
    entities/
    docs/
    claims/
    aliases/
    links/
  derived/
    nodes/
    edges/
    chunks/
    conflicts/
```

The user asked that documents be recorded under `./docs`; therefore this doc is the planning contract, and the future execution workflow can decide whether raw corpora also live under `docs/` or a sibling `corpus/` directory.

## Retrieval Strategy
Use hybrid retrieval:
1. graph neighborhood lookup on canonical entities
2. embedding retrieval on chunks
3. authority-aware reranking
4. answer synthesis with source citations and conflict notes

## Recommended Phase 1 Schema Priorities
Implement schema support first for:
- runes / runewords
- items / unique items / set items / base items
- classes / skills
- monsters / areas / bosses
- cube recipes
- build guides

These domains provide the highest immediate utility for Diablo II QA.
