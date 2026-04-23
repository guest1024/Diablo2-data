CREATE SCHEMA IF NOT EXISTS d2;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS d2.documents (
    doc_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    source_name TEXT,
    label TEXT,
    source_url TEXT NOT NULL,
    local_path TEXT,
    content_type TEXT,
    authority_tier TEXT,
    lane TEXT,
    title TEXT NOT NULL,
    text_content TEXT NOT NULL,
    char_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_documents_source_idx ON d2.documents (source_id);
CREATE INDEX IF NOT EXISTS d2_documents_title_trgm_idx ON d2.documents USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_documents_text_trgm_idx ON d2.documents USING GIN (text_content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_documents_metadata_gin_idx ON d2.documents USING GIN (metadata jsonb_path_ops);

CREATE TABLE IF NOT EXISTS d2.chunks (
    chunk_id TEXT PRIMARY KEY,
    doc_id TEXT NOT NULL REFERENCES d2.documents(doc_id) ON DELETE CASCADE,
    source_id TEXT NOT NULL,
    source_name TEXT,
    source_url TEXT,
    label TEXT,
    title TEXT,
    lane TEXT,
    authority_tier TEXT,
    chunk_index INTEGER NOT NULL,
    text_content TEXT NOT NULL,
    char_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_chunks_doc_idx ON d2.chunks (doc_id, chunk_index);
CREATE INDEX IF NOT EXISTS d2_chunks_source_idx ON d2.chunks (source_id);
CREATE INDEX IF NOT EXISTS d2_chunks_title_trgm_idx ON d2.chunks USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_chunks_text_trgm_idx ON d2.chunks USING GIN (text_content gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_chunks_metadata_gin_idx ON d2.chunks USING GIN (metadata jsonb_path_ops);

CREATE TABLE IF NOT EXISTS d2.search_aliases (
    alias_id TEXT PRIMARY KEY,
    canonical_id TEXT NOT NULL,
    canonical_name TEXT,
    alias TEXT NOT NULL,
    alias_type TEXT,
    node_type TEXT,
    language TEXT,
    confidence NUMERIC(5,4),
    source TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_search_aliases_canonical_idx ON d2.search_aliases (canonical_id);
CREATE INDEX IF NOT EXISTS d2_search_aliases_alias_trgm_idx ON d2.search_aliases USING GIN (alias gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_search_aliases_metadata_gin_idx ON d2.search_aliases USING GIN (metadata jsonb_path_ops);


CREATE TABLE IF NOT EXISTS d2.canonical_entities (
    canonical_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    entity_key TEXT,
    name TEXT NOT NULL,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    document_count INTEGER,
    supporting_source_count INTEGER,
    supporting_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    claim_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_canonical_entities_name_trgm_idx ON d2.canonical_entities USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_canonical_entities_aliases_gin_idx ON d2.canonical_entities USING GIN (aliases jsonb_path_ops);
CREATE INDEX IF NOT EXISTS d2_canonical_entities_type_idx ON d2.canonical_entities (node_type);

CREATE TABLE IF NOT EXISTS d2.canonical_claims (
    canonical_claim_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    subject_type TEXT,
    subject_name TEXT,
    subject_aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    predicate TEXT NOT NULL,
    predicate_family TEXT,
    object_value TEXT,
    supporting_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    supporting_source_count INTEGER,
    claim_variant_count INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_canonical_claims_subject_idx ON d2.canonical_claims (subject_id, predicate);
CREATE INDEX IF NOT EXISTS d2_canonical_claims_predicate_idx ON d2.canonical_claims (predicate, predicate_family);
CREATE INDEX IF NOT EXISTS d2_canonical_claims_object_trgm_idx ON d2.canonical_claims USING GIN (object_value gin_trgm_ops);

CREATE TABLE IF NOT EXISTS d2.provenance (
    provenance_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    source_id TEXT NOT NULL,
    evidence_doc_id TEXT,
    evidence_url TEXT,
    authority_tier TEXT,
    lane TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_provenance_subject_idx ON d2.provenance (subject_id, predicate);
CREATE INDEX IF NOT EXISTS d2_provenance_claim_idx ON d2.provenance (claim_id);
CREATE INDEX IF NOT EXISTS d2_provenance_source_idx ON d2.provenance (source_id, authority_tier);

CREATE TABLE IF NOT EXISTS d2.strategy_edge_facts (
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    object_id TEXT NOT NULL,
    priority INTEGER,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (subject_id, predicate, object_id)
);

CREATE INDEX IF NOT EXISTS d2_strategy_edge_facts_subject_idx ON d2.strategy_edge_facts (subject_id, predicate, priority DESC);
CREATE INDEX IF NOT EXISTS d2_strategy_edge_facts_object_idx ON d2.strategy_edge_facts (object_id, predicate);

CREATE TABLE IF NOT EXISTS d2.build_archetypes (
    build_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    title TEXT,
    class_name TEXT,
    source TEXT,
    source_id TEXT,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS d2.build_core_skills (
    build_id TEXT NOT NULL REFERENCES d2.build_archetypes(build_id) ON DELETE CASCADE,
    skill_name TEXT NOT NULL,
    skill_order INTEGER NOT NULL,
    PRIMARY KEY (build_id, skill_order)
);

CREATE INDEX IF NOT EXISTS d2_build_core_skills_name_idx ON d2.build_core_skills (skill_name);

CREATE TABLE IF NOT EXISTS d2.base_items (
    item_id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    name_zh TEXT,
    bucket TEXT,
    item_type TEXT,
    item_type_2 TEXT,
    normal_code TEXT,
    exceptional_code TEXT,
    elite_code TEXT,
    max_sockets INTEGER,
    level INTEGER,
    level_required INTEGER,
    required_strength INTEGER,
    required_dexterity INTEGER,
    min_armor INTEGER,
    max_armor INTEGER,
    min_damage INTEGER,
    max_damage INTEGER,
    speed INTEGER,
    class_specific BOOLEAN,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_base_items_name_trgm_idx ON d2.base_items USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_base_items_name_zh_trgm_idx ON d2.base_items USING GIN (name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_base_items_bucket_idx ON d2.base_items (bucket);
CREATE INDEX IF NOT EXISTS d2_base_items_item_type_idx ON d2.base_items (item_type);

CREATE TABLE IF NOT EXISTS d2.runes (
    rune_id TEXT PRIMARY KEY,
    rune_key TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    name_zh TEXT,
    level INTEGER,
    level_required INTEGER,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_runes_name_trgm_idx ON d2.runes USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_runes_name_zh_trgm_idx ON d2.runes USING GIN (name_zh gin_trgm_ops);

CREATE TABLE IF NOT EXISTS d2.runewords (
    runeword_id TEXT PRIMARY KEY,
    runeword_key TEXT,
    name TEXT NOT NULL UNIQUE,
    socket_count INTEGER NOT NULL,
    patch_release TEXT,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_runewords_name_trgm_idx ON d2.runewords USING GIN (name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS d2.runeword_runes (
    runeword_id TEXT NOT NULL REFERENCES d2.runewords(runeword_id) ON DELETE CASCADE,
    rune_order INTEGER NOT NULL,
    rune_code TEXT NOT NULL REFERENCES d2.runes(code),
    PRIMARY KEY (runeword_id, rune_order)
);

CREATE INDEX IF NOT EXISTS d2_runeword_runes_rune_idx ON d2.runeword_runes (rune_code);

CREATE TABLE IF NOT EXISTS d2.runeword_item_types (
    runeword_id TEXT NOT NULL REFERENCES d2.runewords(runeword_id) ON DELETE CASCADE,
    item_type_code TEXT NOT NULL,
    PRIMARY KEY (runeword_id, item_type_code)
);

CREATE TABLE IF NOT EXISTS d2.runeword_modifiers (
    runeword_id TEXT NOT NULL REFERENCES d2.runewords(runeword_id) ON DELETE CASCADE,
    modifier_order INTEGER NOT NULL,
    modifier_code TEXT NOT NULL,
    modifier_param TEXT,
    min_value NUMERIC,
    max_value NUMERIC,
    PRIMARY KEY (runeword_id, modifier_order)
);

CREATE INDEX IF NOT EXISTS d2_runeword_modifiers_code_idx ON d2.runeword_modifiers (modifier_code);

CREATE TABLE IF NOT EXISTS d2.skills (
    skill_id TEXT PRIMARY KEY,
    skill_key TEXT,
    name TEXT NOT NULL,
    name_zh TEXT,
    character_class TEXT,
    skill_page INTEGER,
    skill_row INTEGER,
    skill_column INTEGER,
    required_level INTEGER,
    mana_shift INTEGER,
    mana_cost NUMERIC,
    left_skill BOOLEAN,
    passive BOOLEAN,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_skills_name_trgm_idx ON d2.skills USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_skills_name_zh_trgm_idx ON d2.skills USING GIN (name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_skills_class_idx ON d2.skills (character_class);

CREATE TABLE IF NOT EXISTS d2.skill_prerequisites (
    skill_id TEXT NOT NULL REFERENCES d2.skills(skill_id) ON DELETE CASCADE,
    prerequisite_order INTEGER NOT NULL,
    prerequisite_name TEXT NOT NULL,
    prerequisite_skill_id TEXT REFERENCES d2.skills(skill_id),
    PRIMARY KEY (skill_id, prerequisite_order)
);

CREATE INDEX IF NOT EXISTS d2_skill_prereq_name_idx ON d2.skill_prerequisites (prerequisite_name);

CREATE TABLE IF NOT EXISTS d2.cube_recipes (
    recipe_id TEXT PRIMARY KEY,
    row_id TEXT,
    description TEXT NOT NULL,
    recipe_type TEXT,
    enabled BOOLEAN,
    version TEXT,
    num_inputs INTEGER,
    output_code TEXT,
    source TEXT,
    source_file TEXT,
    modifiers JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_cube_recipes_type_idx ON d2.cube_recipes (recipe_type);
CREATE INDEX IF NOT EXISTS d2_cube_recipes_description_trgm_idx ON d2.cube_recipes USING GIN (description gin_trgm_ops);

CREATE TABLE IF NOT EXISTS d2.cube_recipe_inputs (
    recipe_id TEXT NOT NULL REFERENCES d2.cube_recipes(recipe_id) ON DELETE CASCADE,
    input_order INTEGER NOT NULL,
    input_code TEXT NOT NULL,
    PRIMARY KEY (recipe_id, input_order)
);

CREATE INDEX IF NOT EXISTS d2_cube_recipe_inputs_code_idx ON d2.cube_recipe_inputs (input_code);

CREATE TABLE IF NOT EXISTS d2.areas (
    area_id TEXT PRIMARY KEY,
    row_id TEXT,
    level_id INTEGER,
    name TEXT NOT NULL,
    name_zh TEXT,
    act INTEGER,
    is_inside BOOLEAN,
    is_town BOOLEAN,
    level_normal INTEGER,
    level_nightmare INTEGER,
    level_hell INTEGER,
    monster_density_normal INTEGER,
    monster_density_nightmare INTEGER,
    monster_density_hell INTEGER,
    waypoint INTEGER,
    quest INTEGER,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_areas_name_trgm_idx ON d2.areas USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_areas_name_zh_trgm_idx ON d2.areas USING GIN (name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_areas_act_idx ON d2.areas (act);

CREATE TABLE IF NOT EXISTS d2.unique_items (
    unique_item_id TEXT PRIMARY KEY,
    unique_key TEXT,
    name TEXT NOT NULL,
    name_zh TEXT,
    base_code TEXT,
    base_name TEXT,
    base_name_zh TEXT,
    rarity INTEGER,
    level INTEGER,
    level_required INTEGER,
    enabled BOOLEAN,
    cost_multiplier NUMERIC,
    cost_add NUMERIC,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_unique_items_name_trgm_idx ON d2.unique_items USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_unique_items_name_zh_trgm_idx ON d2.unique_items USING GIN (name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_unique_items_base_code_idx ON d2.unique_items (base_code);

CREATE TABLE IF NOT EXISTS d2.monster_resistances (
    monster_id TEXT PRIMARY KEY,
    monster_key TEXT,
    name TEXT NOT NULL,
    name_zh TEXT,
    monster_type TEXT,
    base_id TEXT,
    enabled BOOLEAN,
    source TEXT,
    source_file TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_monsters_name_trgm_idx ON d2.monster_resistances USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_monsters_name_zh_trgm_idx ON d2.monster_resistances USING GIN (name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS d2_monsters_type_idx ON d2.monster_resistances (monster_type);

CREATE TABLE IF NOT EXISTS d2.monster_resistance_values (
    monster_id TEXT NOT NULL REFERENCES d2.monster_resistances(monster_id) ON DELETE CASCADE,
    resistance_type TEXT NOT NULL,
    normal_value NUMERIC,
    nightmare_value NUMERIC,
    hell_value NUMERIC,
    PRIMARY KEY (monster_id, resistance_type)
);

CREATE INDEX IF NOT EXISTS d2_monster_resistance_type_idx ON d2.monster_resistance_values (resistance_type);
CREATE INDEX IF NOT EXISTS d2_monster_resistance_hell_idx ON d2.monster_resistance_values (resistance_type, hell_value);

CREATE TABLE IF NOT EXISTS d2.breakpoints (
    breakpoint_id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    entity_name TEXT NOT NULL,
    source TEXT,
    source_url TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS d2_breakpoints_category_idx ON d2.breakpoints (category);
CREATE INDEX IF NOT EXISTS d2_breakpoints_entity_trgm_idx ON d2.breakpoints USING GIN (entity_name gin_trgm_ops);

CREATE TABLE IF NOT EXISTS d2.breakpoint_points (
    breakpoint_id TEXT NOT NULL REFERENCES d2.breakpoints(breakpoint_id) ON DELETE CASCADE,
    point_order INTEGER NOT NULL,
    breakpoint_value INTEGER NOT NULL,
    frames INTEGER NOT NULL,
    PRIMARY KEY (breakpoint_id, point_order)
);

CREATE INDEX IF NOT EXISTS d2_breakpoint_points_value_idx ON d2.breakpoint_points (breakpoint_id, breakpoint_value);
