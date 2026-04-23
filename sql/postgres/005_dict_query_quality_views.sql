CREATE OR REPLACE VIEW dict.searchable_aliases AS
SELECT
    ad.alias_id,
    COALESCE(ad.term_id, td.term_id) AS term_id,
    ad.canonical_term,
    ad.alias,
    ad.alias_class,
    ad.language,
    ad.confidence,
    ad.rewrite_priority,
    td.term_type,
    td.domain,
    ad.metadata
FROM dict.alias_dictionary ad
LEFT JOIN dict.term_dictionary td ON td.term_id = ad.term_id
WHERE ad.active = TRUE;

CREATE OR REPLACE VIEW qu.best_rewrites AS
SELECT *
FROM (
    SELECT
        qr.*,
        ROW_NUMBER() OVER (
            PARTITION BY qr.query_session_id
            ORDER BY qr.accepted DESC, qr.confidence DESC NULLS LAST, qr.rewrite_rank ASC
        ) AS rn
    FROM qu.query_rewrites qr
) ranked
WHERE rn = 1;

CREATE OR REPLACE VIEW qu.expanded_query_terms AS
SELECT
    qr.query_session_id,
    qr.rewrite_id,
    qr.rewrite_text,
    jsonb_agg(
        jsonb_build_object(
            'term_text', qrt.term_text,
            'term_role', qrt.term_role,
            'source_table', qrt.source_table,
            'source_key', qrt.source_key,
            'confidence', qrt.confidence
        ) ORDER BY qrt.term_order
    ) AS expanded_terms
FROM qu.query_rewrites qr
LEFT JOIN qu.query_rewrite_terms qrt ON qrt.rewrite_id = qr.rewrite_id
GROUP BY qr.query_session_id, qr.rewrite_id, qr.rewrite_text;

CREATE OR REPLACE VIEW qa.answer_citation_coverage AS
SELECT
    ad.answer_draft_id,
    ad.query_session_id,
    ad.draft_status,
    COUNT(ac.citation_order) AS citation_count,
    COUNT(*) FILTER (WHERE ac.verified) AS verified_citation_count,
    ad.unsupported_claim_count,
    ad.missing_citation_count,
    CASE
        WHEN COUNT(ac.citation_order) = 0 THEN 0::NUMERIC
        ELSE ROUND((COUNT(*) FILTER (WHERE ac.verified)::NUMERIC / COUNT(ac.citation_order)::NUMERIC), 4)
    END AS verified_ratio
FROM qa.answer_drafts ad
LEFT JOIN qa.answer_citations ac ON ac.answer_draft_id = ad.answer_draft_id
GROUP BY ad.answer_draft_id, ad.query_session_id, ad.draft_status, ad.unsupported_claim_count, ad.missing_citation_count;

CREATE OR REPLACE VIEW qa.release_gate AS
SELECT
    ad.answer_draft_id,
    ad.query_session_id,
    cov.citation_count,
    cov.verified_citation_count,
    cov.verified_ratio,
    ad.unsupported_claim_count,
    ad.missing_citation_count,
    CASE
        WHEN ad.unsupported_claim_count > 0 THEN FALSE
        WHEN ad.missing_citation_count > 0 THEN FALSE
        WHEN cov.citation_count = 0 THEN FALSE
        WHEN cov.verified_citation_count < cov.citation_count THEN FALSE
        ELSE TRUE
    END AS release_ready
FROM qa.answer_drafts ad
JOIN qa.answer_citation_coverage cov ON cov.answer_draft_id = ad.answer_draft_id;
