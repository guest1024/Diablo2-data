CREATE OR REPLACE VIEW d2.recommended_runeword_builds AS
SELECT
    b.build_id AS subject_id,
    'RECOMMENDS_RUNEWORD'::TEXT AS predicate,
    r.runeword_id AS object_id,
    CASE
        WHEN b.build_id = 'build::hammerdin' AND r.name = 'Enigma' THEN 100
        WHEN b.build_id IN ('build::lightning-sorceress', 'build::nova-sorceress', 'build::blizzard-sorceress') AND r.name = 'Spirit' THEN 90
        WHEN b.build_id = 'build::summon-necromancer' AND r.name = 'Enigma' THEN 85
        ELSE 50
    END AS priority,
    jsonb_build_object('reason', 'derived_build_core_runeword', 'build_id', b.build_id, 'runeword', r.name) AS metadata
FROM d2.build_archetypes b
JOIN d2.runewords r
  ON (b.build_id = 'build::hammerdin' AND r.name = 'Enigma')
  OR (b.build_id IN ('build::lightning-sorceress', 'build::nova-sorceress', 'build::blizzard-sorceress') AND r.name = 'Spirit')
  OR (b.build_id = 'build::summon-necromancer' AND r.name = 'Enigma');

CREATE OR REPLACE VIEW d2.runeword_base_candidates AS
SELECT
    r.runeword_id AS subject_id,
    'RECOMMENDS_BASE'::TEXT AS predicate,
    b.item_id AS object_id,
    CASE
        WHEN r.name = 'Enigma' AND b.name = 'Mage Plate' THEN 100
        WHEN r.name = 'Enigma' AND b.name = 'Dusk Shroud' THEN 95
        WHEN r.name = 'Enigma' AND b.name = 'Archon Plate' THEN 90
        WHEN r.name = 'Spirit' AND b.name = 'Monarch' THEN 100
        ELSE GREATEST(10, 80 - COALESCE(b.required_strength, 0) / 4)
    END AS priority,
    jsonb_build_object('reason', 'derived_base_candidate', 'runeword', r.name, 'base_name', b.name, 'required_strength', b.required_strength, 'max_sockets', b.max_sockets) AS metadata
FROM d2.runewords r
JOIN d2.runeword_item_types rit ON rit.runeword_id = r.runeword_id
JOIN d2.base_items b
  ON b.item_type = rit.item_type_code
 AND COALESCE(b.max_sockets, 0) >= r.socket_count
WHERE (r.name = 'Enigma' AND b.name IN ('Mage Plate', 'Dusk Shroud', 'Archon Plate'))
   OR (r.name = 'Spirit' AND b.name IN ('Monarch', 'Crystal Sword'));

CREATE OR REPLACE VIEW d2.base_farm_area_candidates AS
SELECT
    b.item_id AS subject_id,
    'FARMS_IN_AREA'::TEXT AS predicate,
    a.area_id AS object_id,
    CASE
        WHEN a.name = 'The Secret Cow Level' THEN 100
        WHEN a.name = 'Ancient Tunnels' THEN 95
        WHEN a.name = 'Pit Level 1' THEN 90
        WHEN a.name = 'Pit Level 2' THEN 88
        ELSE 50
    END AS priority,
    jsonb_build_object('reason', 'derived_base_farm_area', 'base_name', b.name, 'area_name', a.name, 'level_hell', a.level_hell, 'monster_density_hell', a.monster_density_hell) AS metadata
FROM d2.base_items b
JOIN d2.areas a ON a.name IN ('The Secret Cow Level', 'Ancient Tunnels', 'Pit Level 1', 'Pit Level 2')
WHERE b.name IN ('Mage Plate', 'Dusk Shroud', 'Archon Plate', 'Monarch');

CREATE OR REPLACE VIEW d2.build_breakpoint_targets AS
SELECT
    b.build_id AS subject_id,
    'REQUIRES_BREAKPOINT'::TEXT AS predicate,
    bp.breakpoint_id AS object_id,
    CASE
        WHEN b.build_id IN ('build::lightning-sorceress','build::nova-sorceress') AND bp.entity_name = 'Sorceress (Lightning / Chain Lightning)' AND bp.category = 'FCR' THEN 100
        WHEN b.build_id = 'build::blizzard-sorceress' AND bp.entity_name = 'Sorceress' AND bp.category = 'FCR' THEN 95
        WHEN b.build_id = 'build::hammerdin' AND bp.entity_name = 'Paladin' AND bp.category = 'FCR' THEN 95
        ELSE 70
    END AS priority,
    jsonb_build_object('reason','derived_breakpoint_target','build_id',b.build_id,'breakpoint',bp.entity_name,'category',bp.category) AS metadata
FROM d2.build_archetypes b
JOIN d2.breakpoints bp
  ON (b.build_id IN ('build::lightning-sorceress','build::nova-sorceress') AND bp.entity_name = 'Sorceress (Lightning / Chain Lightning)' AND bp.category = 'FCR')
  OR (b.build_id = 'build::blizzard-sorceress' AND bp.entity_name = 'Sorceress' AND bp.category = 'FCR')
  OR (b.build_id = 'build::hammerdin' AND bp.entity_name = 'Paladin' AND bp.category = 'FCR');

CREATE OR REPLACE VIEW d2.runeword_roll_benefits AS
SELECT
    r.runeword_id AS subject_id,
    'BENEFITS_FROM_ROLL'::TEXT AS predicate,
    rd.rule_id AS object_id,
    CASE
        WHEN r.name = 'Spirit' THEN 100
        ELSE 80
    END AS priority,
    jsonb_build_object('reason','derived_runeword_roll_rule','runeword',r.name,'rule_id',rd.rule_id) AS metadata
FROM d2.runewords r
JOIN dict.rule_dictionary rd
  ON rd.rule_type = 'runeword_modifier'
 AND rd.canonical_subject = r.name
WHERE r.name IN ('Spirit', 'Enigma');

CREATE OR REPLACE VIEW d2.good_base_for_build AS
SELECT
    b.build_id AS subject_id,
    'GOOD_FOR_BUILD'::TEXT AS predicate,
    base.item_id AS object_id,
    CASE
        WHEN b.build_id = 'build::hammerdin' AND base.name = 'Mage Plate' THEN 100
        WHEN b.build_id = 'build::hammerdin' AND base.name = 'Dusk Shroud' THEN 90
        WHEN b.build_id IN ('build::lightning-sorceress','build::blizzard-sorceress','build::nova-sorceress') AND base.name = 'Monarch' THEN 95
        ELSE 70
    END AS priority,
    jsonb_build_object('reason','derived_good_base_for_build','build_id',b.build_id,'base_name',base.name) AS metadata
FROM d2.build_archetypes b
JOIN d2.base_items base
  ON (b.build_id = 'build::hammerdin' AND base.name IN ('Mage Plate','Dusk Shroud','Archon Plate'))
  OR (b.build_id IN ('build::lightning-sorceress','build::blizzard-sorceress','build::nova-sorceress') AND base.name IN ('Monarch','Crystal Sword'));

CREATE OR REPLACE VIEW d2.good_runeword_for_class AS
SELECT
    b.build_id AS subject_id,
    'GOOD_FOR_CLASS'::TEXT AS predicate,
    r.runeword_id AS object_id,
    CASE
        WHEN b.class_name = 'Sorceress' AND r.name = 'Spirit' THEN 100
        WHEN b.class_name = 'Paladin' AND r.name = 'Enigma' THEN 95
        WHEN b.class_name = 'Necromancer' AND r.name = 'Enigma' THEN 90
        ELSE 60
    END AS priority,
    jsonb_build_object('reason','derived_good_runeword_for_class','class_name',b.class_name,'runeword',r.name) AS metadata
FROM d2.build_archetypes b
JOIN d2.runewords r
  ON (b.class_name = 'Sorceress' AND r.name = 'Spirit')
  OR (b.class_name = 'Paladin' AND r.name = 'Enigma')
  OR (b.class_name = 'Necromancer' AND r.name = 'Enigma');

CREATE OR REPLACE VIEW d2.good_farm_target_for_build AS
SELECT
    b.build_id AS subject_id,
    'GOOD_FOR_FARM_TARGET'::TEXT AS predicate,
    a.area_id AS object_id,
    CASE
        WHEN b.build_id = 'build::hammerdin' AND a.name = 'The Secret Cow Level' THEN 100
        WHEN b.build_id = 'build::hammerdin' AND a.name = 'Pit Level 1' THEN 95
        WHEN b.build_id = 'build::hammerdin' AND a.name = 'Ancient Tunnels' THEN 90
        WHEN b.build_id IN ('build::lightning-sorceress','build::blizzard-sorceress','build::nova-sorceress') AND a.name = 'Ancient Tunnels' THEN 100
        ELSE 70
    END AS priority,
    jsonb_build_object('reason','derived_good_farm_target_for_build','build_id',b.build_id,'area_name',a.name) AS metadata
FROM d2.build_archetypes b
JOIN d2.areas a
  ON (b.build_id = 'build::hammerdin' AND a.name IN ('The Secret Cow Level','Pit Level 1','Ancient Tunnels'))
  OR (b.build_id IN ('build::lightning-sorceress','build::blizzard-sorceress','build::nova-sorceress') AND a.name IN ('Ancient Tunnels','The Secret Cow Level'));

CREATE OR REPLACE VIEW d2.strategy_object_catalog AS
SELECT breakpoint_id AS object_id, entity_name || ' ' || category AS name
FROM d2.breakpoints
UNION ALL
SELECT rule_id AS object_id, COALESCE(canonical_subject, description) AS name
FROM dict.rule_dictionary
WHERE active = TRUE;

CREATE OR REPLACE VIEW d2.strategy_edges AS
SELECT * FROM d2.recommended_runeword_builds
UNION ALL
SELECT * FROM d2.runeword_base_candidates
UNION ALL
SELECT * FROM d2.base_farm_area_candidates
UNION ALL
SELECT * FROM d2.build_breakpoint_targets
UNION ALL
SELECT * FROM d2.runeword_roll_benefits
UNION ALL
SELECT * FROM d2.good_base_for_build
UNION ALL
SELECT * FROM d2.good_runeword_for_class
UNION ALL
SELECT * FROM d2.good_farm_target_for_build;
