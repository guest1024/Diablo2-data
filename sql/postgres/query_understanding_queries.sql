-- 1) 黑话输入 -> trigram alias + rewrite term expansion
SELECT alias_id, canonical_term, alias, alias_class, confidence, rewrite_priority,
       similarity(alias, '劳模掉不掉军帽') AS sim
FROM dict.searchable_aliases
WHERE alias % '劳模掉不掉军帽'
ORDER BY rewrite_priority ASC, sim DESC, confidence DESC NULLS LAST
LIMIT 20;

-- 2) 查看一个 query session 的最佳 rewrite
SELECT query_session_id, rewrite_text, rewrite_kind, confidence, recall_expectation, precision_expectation
FROM qu.best_rewrites
WHERE query_session_id = '00000000-0000-0000-0000-000000000000';

-- 3) 查看 rewrite 展开的词项是否包含 canonical/alias/constraint
SELECT *
FROM qu.expanded_query_terms
WHERE query_session_id = '00000000-0000-0000-0000-000000000000';

-- 4) 递归查看一个 subquestion plan 的依赖链
WITH RECURSIVE step_tree AS (
    SELECT
        s.plan_id,
        s.step_order,
        s.subquestion_text,
        s.dependency_steps,
        0 AS depth
    FROM qu.subquestion_steps s
    WHERE s.plan_id = '00000000-0000-0000-0000-000000000000'::uuid
      AND jsonb_array_length(s.dependency_steps) = 0

    UNION ALL

    SELECT
        child.plan_id,
        child.step_order,
        child.subquestion_text,
        child.dependency_steps,
        parent.depth + 1
    FROM qu.subquestion_steps child
    JOIN step_tree parent
      ON child.plan_id = parent.plan_id
     AND child.dependency_steps @> to_jsonb(ARRAY[parent.step_order])
)
SELECT *
FROM step_tree
ORDER BY depth, step_order;

-- 5) 对某个 answer draft 做 release gate 检查
SELECT *
FROM qa.release_gate
WHERE answer_draft_id = '00000000-0000-0000-0000-000000000000';

-- 6) 找出“已生成答案但引用未通过校验”的 draft
SELECT
    ad.answer_draft_id,
    ad.query_session_id,
    ad.draft_status,
    rg.citation_count,
    rg.verified_citation_count,
    rg.verified_ratio,
    rg.release_ready
FROM qa.answer_drafts ad
JOIN qa.release_gate rg ON rg.answer_draft_id = ad.answer_draft_id
WHERE rg.release_ready = FALSE
ORDER BY ad.created_at DESC;
