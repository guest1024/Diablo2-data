\set ON_ERROR_STOP on
BEGIN;
TRUNCATE TABLE qu.answer_constraints CASCADE;
TRUNCATE TABLE qu.retrieval_policies CASCADE;
TRUNCATE TABLE dict.query_pattern_dictionary CASCADE;
TRUNCATE TABLE dict.rule_dictionary CASCADE;
TRUNCATE TABLE dict.monster_dictionary CASCADE;
TRUNCATE TABLE dict.area_dictionary CASCADE;
TRUNCATE TABLE dict.item_dictionary CASCADE;
TRUNCATE TABLE dict.build_dictionary_skills CASCADE;
TRUNCATE TABLE dict.build_dictionary CASCADE;
TRUNCATE TABLE dict.alias_dictionary CASCADE;
TRUNCATE TABLE dict.term_dictionary CASCADE;
\copy dict.term_dictionary (term_id, canonical_term, canonical_term_zh, term_type, domain, language, description, source, confidence, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/term_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.alias_dictionary (alias_id, term_id, canonical_term, alias, alias_class, language, community_frequency, confidence, source, active, rewrite_priority, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/alias_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.build_dictionary (build_id, class_name, build_name, build_name_zh, aliases, source, confidence, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/build_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.build_dictionary_skills (build_id, skill_order, skill_name) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/build_dictionary_skills.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.item_dictionary (item_id, canonical_name, canonical_name_zh, item_family, rarity, base_code, normalized_keywords, source, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/item_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.area_dictionary (area_id, canonical_name, canonical_name_zh, act, area_tags, farm_tags, source, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/area_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.monster_dictionary (monster_id, canonical_name, canonical_name_zh, monster_type, monster_tags, source, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/monster_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.rule_dictionary (rule_id, rule_type, subject_type, canonical_subject, description, rule_jsonb, source, confidence, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/rule_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy dict.query_pattern_dictionary (pattern_id, query_type, trigger_phrase, intent_label, expansion_policy, requires_subquestions, requires_numeric_guard, requires_citation_verification, lane_hints, source, active, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/query_pattern_dictionary.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy qu.retrieval_policies (policy_id, policy_name, query_type, min_alias_lane, min_bm25_lane, min_vector_lane, min_graph_lane, require_authority_rerank, require_numeric_grounding, require_citation_verification, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/retrieval_policies.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
\copy qu.answer_constraints (constraint_id, query_type, must_quote_sources, must_verify_numeric_claims, must_disclose_conflicts, forbid_uncited_facts, forbid_linear_interpolation_without_rule, metadata) FROM '/home/user/diablo2-data/docs/tier0/postgres-dict-bundle/data/answer_constraints.tsv' WITH (FORMAT csv, DELIMITER E'\t', QUOTE '"', NULL '\N')
COMMIT;
