-- 1) 黑话 / 错别字 / 缩写：使用 pg_trgm 检索 alias。
SELECT canonical_name, alias, similarity(alias, '劳模') AS sim
FROM d2.search_aliases
WHERE alias % '劳模'
ORDER BY sim DESC, canonical_name
LIMIT 10;

-- 2) 给定当前持有符文，列出还能做哪些符文之语，以及缺哪些符文。
WITH inventory(rune_code, qty) AS (
    VALUES ('r30', 1)  -- Ber
),
missing AS (
    SELECT
        rr.runeword_id,
        rr.runeword_name,
        rr.rune_code,
        rr.rune_name,
        rr.required_count,
        GREATEST(rr.required_count - COALESCE(i.qty, 0), 0) AS missing_count
    FROM d2.runeword_missing_runes rr
    LEFT JOIN inventory i ON i.rune_code = rr.rune_code
),
scored AS (
    SELECT
        runeword_id,
        runeword_name,
        SUM(missing_count) AS total_missing,
        JSONB_AGG(
            JSONB_BUILD_OBJECT(
                'rune_code', rune_code,
                'rune_name', rune_name,
                'missing_count', missing_count
            ) ORDER BY rune_name
        ) FILTER (WHERE missing_count > 0) AS missing_runes
    FROM missing
    GROUP BY runeword_id, runeword_name
)
SELECT *
FROM scored
ORDER BY total_missing, runeword_name;

-- 3) 递归展开技能前置链：Blessed Hammer 需要什么前置技能。
WITH RECURSIVE prereq_tree AS (
    SELECT
        s.skill_id AS root_skill_id,
        s.name AS root_skill_name,
        sp.prerequisite_skill_id,
        sp.prerequisite_name,
        1 AS depth,
        ARRAY[LOWER(s.name), LOWER(sp.prerequisite_name)]::TEXT[] AS visit_path
    FROM d2.skills s
    JOIN d2.skill_prerequisites sp ON sp.skill_id = s.skill_id
    WHERE LOWER(s.name) = LOWER('Blessed Hammer')

    UNION ALL

    SELECT
        pt.root_skill_id,
        pt.root_skill_name,
        sp.prerequisite_skill_id,
        sp.prerequisite_name,
        pt.depth + 1,
        pt.visit_path || LOWER(sp.prerequisite_name)
    FROM prereq_tree pt
    JOIN d2.skills s ON LOWER(s.name) = LOWER(pt.prerequisite_name)
    JOIN d2.skill_prerequisites sp ON sp.skill_id = s.skill_id
    WHERE NOT LOWER(sp.prerequisite_name) = ANY(pt.visit_path)
)
SELECT root_skill_name, prerequisite_name, depth
FROM prereq_tree
ORDER BY depth, prerequisite_name;

-- 4) 计算 FCR 是否跨档：法师 90 FCR + Spirit 最低 25 FCR => 是否超过下一档 105。
WITH current_state AS (
    SELECT 90::INTEGER AS current_fcr, 25::INTEGER AS additional_fcr
),
entity AS (
    SELECT breakpoint_id
    FROM d2.breakpoints
    WHERE category = 'FCR' AND entity_name = 'Sorceress'
),
points AS (
    SELECT bp.breakpoint_value, bp.frames
    FROM d2.breakpoint_points bp
    JOIN entity e ON e.breakpoint_id = bp.breakpoint_id
),
calc AS (
    SELECT
        cs.current_fcr,
        cs.additional_fcr,
        cs.current_fcr + cs.additional_fcr AS total_fcr
    FROM current_state cs
)
SELECT
    c.current_fcr,
    c.additional_fcr,
    c.total_fcr,
    (
        SELECT p.breakpoint_value
        FROM points p
        WHERE p.breakpoint_value > c.current_fcr
        ORDER BY p.breakpoint_value
        LIMIT 1
    ) AS next_breakpoint_before,
    (
        SELECT p.breakpoint_value
        FROM points p
        WHERE p.breakpoint_value <= c.total_fcr
        ORDER BY p.breakpoint_value DESC
        LIMIT 1
    ) AS achieved_breakpoint_after
FROM calc c;

-- 5) 查询地穴 / The Pit 的地狱等级与场景信息。
SELECT area_id, name, name_zh, act, level_hell, monster_density_hell
FROM d2.areas
WHERE LOWER(name) LIKE '%pit%'
ORDER BY level_hell DESC, name;

-- 6) 查某个怪物在地狱难度下的抗性。
SELECT m.name, m.name_zh, rv.resistance_type, rv.hell_value
FROM d2.monster_resistances m
JOIN d2.monster_resistance_values rv ON rv.monster_id = m.monster_id
WHERE LOWER(m.name) = LOWER('Mephisto')
ORDER BY rv.resistance_type;
