CREATE OR REPLACE VIEW d2.entity_catalog AS
SELECT node_type::TEXT AS entity_type, canonical_id AS entity_id, name, NULL::TEXT AS name_zh,
       jsonb_build_object('entity_key', entity_key, 'document_count', document_count, 'supporting_source_count', supporting_source_count) AS metadata
FROM d2.canonical_entities
UNION ALL
SELECT 'Runeword'::TEXT AS entity_type, runeword_id AS entity_id, name, NULL::TEXT AS name_zh, jsonb_build_object('socket_count', socket_count, 'patch_release', patch_release) AS metadata
FROM d2.runewords
UNION ALL
SELECT 'Rune', rune_id, name, name_zh, jsonb_build_object('code', code, 'level_required', level_required)
FROM d2.runes
UNION ALL
SELECT 'BaseItem', item_id, name, name_zh, jsonb_build_object('code', code, 'bucket', bucket, 'max_sockets', max_sockets)
FROM d2.base_items
UNION ALL
SELECT 'UniqueItem', unique_item_id, name, name_zh, jsonb_build_object('base_code', base_code, 'base_name', base_name)
FROM d2.unique_items
UNION ALL
SELECT 'Skill', skill_id, name, name_zh, jsonb_build_object('character_class', character_class, 'required_level', required_level)
FROM d2.skills
UNION ALL
SELECT 'Area', area_id, name, name_zh, jsonb_build_object('act', act, 'level_hell', level_hell)
FROM d2.areas
UNION ALL
SELECT 'Monster', monster_id, name, name_zh, jsonb_build_object('monster_type', monster_type)
FROM d2.monster_resistances
UNION ALL
SELECT 'Build', build_id, canonical_name AS name, NULL::TEXT AS name_zh, jsonb_build_object('class_name', class_name, 'title', title)
FROM d2.build_archetypes;

CREATE OR REPLACE VIEW d2.gameplay_edges AS
SELECT rw.runeword_id AS subject_id, 'USES_RUNE'::TEXT AS predicate, r.rune_id AS object_id,
       jsonb_build_object('rune_order', rr.rune_order, 'rune_code', rr.rune_code) AS metadata
FROM d2.runeword_runes rr
JOIN d2.runewords rw ON rw.runeword_id = rr.runeword_id
JOIN d2.runes r ON r.code = rr.rune_code
UNION ALL
SELECT rw.runeword_id, 'REQUIRES_ITEM_TYPE', rit.item_type_code,
       jsonb_build_object('item_type_code', rit.item_type_code)
FROM d2.runeword_item_types rit
JOIN d2.runewords rw ON rw.runeword_id = rit.runeword_id
UNION ALL
SELECT s.skill_id, 'REQUIRES_SKILL', COALESCE(sp.prerequisite_skill_id, sp.prerequisite_name),
       jsonb_build_object('prerequisite_order', sp.prerequisite_order, 'prerequisite_name', sp.prerequisite_name)
FROM d2.skill_prerequisites sp
JOIN d2.skills s ON s.skill_id = sp.skill_id
UNION ALL
SELECT bcs.build_id, 'USES_SKILL', s.skill_id,
       jsonb_build_object('skill_order', bcs.skill_order, 'skill_name', bcs.skill_name)
FROM d2.build_core_skills bcs
LEFT JOIN d2.skills s ON lower(s.name) = lower(bcs.skill_name);

CREATE OR REPLACE VIEW d2.runeword_missing_runes AS
SELECT
    rw.runeword_id,
    rw.name AS runeword_name,
    r.rune_id,
    r.code AS rune_code,
    r.name AS rune_name,
    COUNT(*)::INTEGER AS required_count
FROM d2.runewords rw
JOIN d2.runeword_runes rr ON rr.runeword_id = rw.runeword_id
JOIN d2.runes r ON r.code = rr.rune_code
GROUP BY rw.runeword_id, rw.name, r.rune_id, r.code, r.name;

CREATE OR REPLACE VIEW d2.grounded_claims AS
SELECT
    cc.canonical_claim_id,
    cc.subject_id,
    cc.subject_type,
    cc.subject_name,
    cc.predicate,
    cc.predicate_family,
    cc.object_value,
    cc.supporting_sources,
    cc.supporting_source_count,
    p.provenance_id,
    p.claim_id,
    p.source_id,
    p.evidence_doc_id,
    p.evidence_url,
    p.authority_tier,
    p.lane
FROM d2.canonical_claims cc
LEFT JOIN d2.provenance p
  ON p.subject_id = cc.subject_id
 AND p.predicate = cc.predicate;
