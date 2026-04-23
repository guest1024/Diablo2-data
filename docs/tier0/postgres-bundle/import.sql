\set ON_ERROR_STOP on
BEGIN;
TRUNCATE TABLE d2.breakpoint_points CASCADE;
TRUNCATE TABLE d2.breakpoints CASCADE;
TRUNCATE TABLE d2.monster_resistance_values CASCADE;
TRUNCATE TABLE d2.monster_resistances CASCADE;
TRUNCATE TABLE d2.unique_items CASCADE;
TRUNCATE TABLE d2.areas CASCADE;
TRUNCATE TABLE d2.cube_recipe_inputs CASCADE;
TRUNCATE TABLE d2.cube_recipes CASCADE;
TRUNCATE TABLE d2.skill_prerequisites CASCADE;
TRUNCATE TABLE d2.skills CASCADE;
TRUNCATE TABLE d2.runeword_modifiers CASCADE;
TRUNCATE TABLE d2.runeword_item_types CASCADE;
TRUNCATE TABLE d2.runeword_runes CASCADE;
TRUNCATE TABLE d2.runewords CASCADE;
TRUNCATE TABLE d2.runes CASCADE;
TRUNCATE TABLE d2.base_items CASCADE;
TRUNCATE TABLE d2.build_core_skills CASCADE;
TRUNCATE TABLE d2.build_archetypes CASCADE;
TRUNCATE TABLE d2.search_aliases CASCADE;
TRUNCATE TABLE d2.provenance CASCADE;
TRUNCATE TABLE d2.canonical_claims CASCADE;
TRUNCATE TABLE d2.canonical_entities CASCADE;
TRUNCATE TABLE d2.chunks CASCADE;
TRUNCATE TABLE d2.documents CASCADE;
\copy d2.documents (doc_id, source_id, source_name, label, source_url, local_path, content_type, authority_tier, lane, title, text_content, char_count, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/documents.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.chunks (chunk_id, doc_id, source_id, source_name, source_url, label, title, lane, authority_tier, chunk_index, text_content, char_count, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/chunks.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.canonical_entities (canonical_id, node_type, entity_key, name, aliases, document_count, supporting_source_count, supporting_sources, claim_count, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/canonical_entities.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.canonical_claims (canonical_claim_id, subject_id, subject_type, subject_name, subject_aliases, predicate, predicate_family, object_value, supporting_sources, supporting_source_count, claim_variant_count, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/canonical_claims.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.provenance (provenance_id, claim_id, subject_id, predicate, source_id, evidence_doc_id, evidence_url, authority_tier, lane, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/provenance.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.search_aliases (alias_id, canonical_id, canonical_name, alias, alias_type, node_type, language, confidence, source, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/search_aliases.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.build_archetypes (build_id, canonical_name, title, class_name, source, source_id, aliases, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/build_archetypes.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.build_core_skills (build_id, skill_name, skill_order) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/build_core_skills.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.base_items (item_id, code, name, name_zh, bucket, item_type, item_type_2, normal_code, exceptional_code, elite_code, max_sockets, level, level_required, required_strength, required_dexterity, min_armor, max_armor, min_damage, max_damage, speed, class_specific, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/base_items.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.runes (rune_id, rune_key, code, name, name_zh, level, level_required, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/runes.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.runewords (runeword_id, runeword_key, name, socket_count, patch_release, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/runewords.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.runeword_runes (runeword_id, rune_order, rune_code) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/runeword_runes.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.runeword_item_types (runeword_id, item_type_code) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/runeword_item_types.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.runeword_modifiers (runeword_id, modifier_order, modifier_code, modifier_param, min_value, max_value) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/runeword_modifiers.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.skills (skill_id, skill_key, name, name_zh, character_class, skill_page, skill_row, skill_column, required_level, mana_shift, mana_cost, left_skill, passive, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/skills.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.skill_prerequisites (skill_id, prerequisite_order, prerequisite_name, prerequisite_skill_id) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/skill_prerequisites.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.cube_recipes (recipe_id, row_id, description, recipe_type, enabled, version, num_inputs, output_code, source, source_file, modifiers, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/cube_recipes.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.cube_recipe_inputs (recipe_id, input_order, input_code) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/cube_recipe_inputs.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.areas (area_id, row_id, level_id, name, name_zh, act, is_inside, is_town, level_normal, level_nightmare, level_hell, monster_density_normal, monster_density_nightmare, monster_density_hell, waypoint, quest, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/areas.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.unique_items (unique_item_id, unique_key, name, name_zh, base_code, base_name, base_name_zh, rarity, level, level_required, enabled, cost_multiplier, cost_add, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/unique_items.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.monster_resistances (monster_id, monster_key, name, name_zh, monster_type, base_id, enabled, source, source_file, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/monster_resistances.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.monster_resistance_values (monster_id, resistance_type, normal_value, nightmare_value, hell_value) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/monster_resistance_values.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.breakpoints (breakpoint_id, category, entity_name, source, source_url, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/breakpoints.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy d2.breakpoint_points (breakpoint_id, point_order, breakpoint_value, frames) FROM '/home/user/diablo2-data/docs/tier0/postgres-bundle/data/breakpoint_points.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
COMMIT;
