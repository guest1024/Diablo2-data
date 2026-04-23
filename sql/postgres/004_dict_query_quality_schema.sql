CREATE SCHEMA IF NOT EXISTS dict;
CREATE SCHEMA IF NOT EXISTS qu;
CREATE SCHEMA IF NOT EXISTS qa;

CREATE TABLE IF NOT EXISTS dict.term_dictionary (
    term_id TEXT PRIMARY KEY,
    canonical_term TEXT NOT NULL,
    canonical_term_zh TEXT,
    term_type TEXT NOT NULL,
    domain TEXT,
    language TEXT,
    description TEXT,
    source TEXT,
    confidence NUMERIC(5,4),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_term_dictionary_term_trgm_idx ON dict.term_dictionary USING GIN (canonical_term gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_term_dictionary_term_zh_trgm_idx ON dict.term_dictionary USING GIN (canonical_term_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_term_dictionary_type_idx ON dict.term_dictionary (term_type);

CREATE TABLE IF NOT EXISTS dict.alias_dictionary (
    alias_id TEXT PRIMARY KEY,
    term_id TEXT REFERENCES dict.term_dictionary(term_id) ON DELETE SET NULL,
    canonical_term TEXT NOT NULL,
    alias TEXT NOT NULL,
    alias_norm TEXT GENERATED ALWAYS AS (lower(alias)) STORED,
    alias_class TEXT NOT NULL,
    language TEXT,
    community_frequency NUMERIC,
    confidence NUMERIC(5,4),
    source TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    rewrite_priority INTEGER NOT NULL DEFAULT 100,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_alias_dictionary_alias_trgm_idx ON dict.alias_dictionary USING GIN (alias gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_alias_dictionary_alias_norm_idx ON dict.alias_dictionary (alias_norm);
CREATE INDEX IF NOT EXISTS dict_alias_dictionary_canonical_idx ON dict.alias_dictionary (canonical_term);

CREATE TABLE IF NOT EXISTS dict.build_dictionary (
    build_id TEXT PRIMARY KEY,
    class_name TEXT,
    build_name TEXT NOT NULL,
    build_name_zh TEXT,
    aliases JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    confidence NUMERIC(5,4),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_build_dictionary_name_trgm_idx ON dict.build_dictionary USING GIN (build_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_build_dictionary_name_zh_trgm_idx ON dict.build_dictionary USING GIN (build_name_zh gin_trgm_ops);

CREATE TABLE IF NOT EXISTS dict.build_dictionary_skills (
    build_id TEXT NOT NULL REFERENCES dict.build_dictionary(build_id) ON DELETE CASCADE,
    skill_order INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    PRIMARY KEY (build_id, skill_order)
);

CREATE TABLE IF NOT EXISTS dict.item_dictionary (
    item_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    canonical_name_zh TEXT,
    item_family TEXT NOT NULL,
    rarity TEXT,
    base_code TEXT,
    normalized_keywords JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_item_dictionary_name_trgm_idx ON dict.item_dictionary USING GIN (canonical_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_item_dictionary_name_zh_trgm_idx ON dict.item_dictionary USING GIN (canonical_name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_item_dictionary_family_idx ON dict.item_dictionary (item_family, rarity);

CREATE TABLE IF NOT EXISTS dict.area_dictionary (
    area_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    canonical_name_zh TEXT,
    act INTEGER,
    area_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    farm_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_area_dictionary_name_trgm_idx ON dict.area_dictionary USING GIN (canonical_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_area_dictionary_name_zh_trgm_idx ON dict.area_dictionary USING GIN (canonical_name_zh gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_area_dictionary_act_idx ON dict.area_dictionary (act);

CREATE TABLE IF NOT EXISTS dict.monster_dictionary (
    monster_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    canonical_name_zh TEXT,
    monster_type TEXT,
    monster_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_monster_dictionary_name_trgm_idx ON dict.monster_dictionary USING GIN (canonical_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS dict_monster_dictionary_name_zh_trgm_idx ON dict.monster_dictionary USING GIN (canonical_name_zh gin_trgm_ops);

CREATE TABLE IF NOT EXISTS dict.rule_dictionary (
    rule_id TEXT PRIMARY KEY,
    rule_type TEXT NOT NULL,
    subject_type TEXT,
    canonical_subject TEXT,
    description TEXT NOT NULL,
    rule_jsonb JSONB NOT NULL DEFAULT '{}'::jsonb,
    source TEXT,
    confidence NUMERIC(5,4),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_rule_dictionary_type_idx ON dict.rule_dictionary (rule_type, subject_type);
CREATE INDEX IF NOT EXISTS dict_rule_dictionary_subject_trgm_idx ON dict.rule_dictionary USING GIN (canonical_subject gin_trgm_ops);

CREATE TABLE IF NOT EXISTS dict.query_pattern_dictionary (
    pattern_id TEXT PRIMARY KEY,
    query_type TEXT NOT NULL,
    trigger_phrase TEXT,
    intent_label TEXT NOT NULL,
    expansion_policy TEXT,
    requires_subquestions BOOLEAN NOT NULL DEFAULT FALSE,
    requires_numeric_guard BOOLEAN NOT NULL DEFAULT FALSE,
    requires_citation_verification BOOLEAN NOT NULL DEFAULT TRUE,
    lane_hints JSONB NOT NULL DEFAULT '[]'::jsonb,
    source TEXT,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS dict_query_pattern_type_idx ON dict.query_pattern_dictionary (query_type, intent_label);
CREATE INDEX IF NOT EXISTS dict_query_pattern_trigger_trgm_idx ON dict.query_pattern_dictionary USING GIN (trigger_phrase gin_trgm_ops);

CREATE TABLE IF NOT EXISTS qu.query_sessions (
    query_session_id UUID PRIMARY KEY,
    raw_query TEXT NOT NULL,
    query_language TEXT,
    user_context JSONB NOT NULL DEFAULT '{}'::jsonb,
    strict_mode BOOLEAN NOT NULL DEFAULT TRUE,
    status TEXT NOT NULL DEFAULT 'received' CHECK (status IN ('received', 'rewritten', 'planned', 'retrieved', 'answered', 'verified', 'failed')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qu.query_rewrites (
    rewrite_id UUID PRIMARY KEY,
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    rewrite_text TEXT NOT NULL,
    rewrite_kind TEXT NOT NULL CHECK (rewrite_kind IN ('identity', 'alias_normalized', 'term_expanded', 'entity_targeted', 'subquestion_seed', 'safety_rewrite')),
    rewrite_rank INTEGER NOT NULL,
    accepted BOOLEAN NOT NULL DEFAULT FALSE,
    confidence NUMERIC(5,4),
    recall_expectation NUMERIC(5,4),
    precision_expectation NUMERIC(5,4),
    rationale TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS qu_query_rewrites_session_idx ON qu.query_rewrites (query_session_id, rewrite_rank);
CREATE INDEX IF NOT EXISTS qu_query_rewrites_text_trgm_idx ON qu.query_rewrites USING GIN (rewrite_text gin_trgm_ops);

CREATE TABLE IF NOT EXISTS qu.query_rewrite_terms (
    rewrite_id UUID NOT NULL REFERENCES qu.query_rewrites(rewrite_id) ON DELETE CASCADE,
    term_order INTEGER NOT NULL,
    term_text TEXT NOT NULL,
    term_role TEXT NOT NULL CHECK (term_role IN ('original', 'alias', 'canonical', 'hint', 'constraint', 'negative_constraint', 'lane_hint')),
    source_table TEXT,
    source_key TEXT,
    confidence NUMERIC(5,4),
    PRIMARY KEY (rewrite_id, term_order)
);

CREATE TABLE IF NOT EXISTS qu.entity_resolution_candidates (
    candidate_id UUID PRIMARY KEY,
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    rewrite_id UUID REFERENCES qu.query_rewrites(rewrite_id) ON DELETE SET NULL,
    candidate_entity_type TEXT,
    candidate_entity_id TEXT,
    candidate_name TEXT NOT NULL,
    resolution_method TEXT NOT NULL CHECK (resolution_method IN ('exact_alias', 'trigram_alias', 'bm25', 'vector', 'graph_neighbor', 'manual_seed')),
    score NUMERIC(10,6),
    accepted BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS qu_entity_resolution_session_idx ON qu.entity_resolution_candidates (query_session_id, accepted, score DESC);

CREATE TABLE IF NOT EXISTS qu.subquestion_plans (
    plan_id UUID PRIMARY KEY,
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    plan_title TEXT NOT NULL,
    plan_status TEXT NOT NULL DEFAULT 'draft' CHECK (plan_status IN ('draft', 'approved', 'executing', 'complete', 'failed')),
    requires_graph_expansion BOOLEAN NOT NULL DEFAULT FALSE,
    requires_numeric_lookup BOOLEAN NOT NULL DEFAULT FALSE,
    requires_citation_verification BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qu.subquestion_steps (
    plan_id UUID NOT NULL REFERENCES qu.subquestion_plans(plan_id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    subquestion_text TEXT NOT NULL,
    expected_answer_type TEXT,
    required_lane TEXT,
    dependency_steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'done', 'failed', 'skipped')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (plan_id, step_order)
);

CREATE TABLE IF NOT EXISTS qu.retrieval_policies (
    policy_id TEXT PRIMARY KEY,
    policy_name TEXT NOT NULL,
    query_type TEXT,
    min_alias_lane INTEGER NOT NULL DEFAULT 5,
    min_bm25_lane INTEGER NOT NULL DEFAULT 10,
    min_vector_lane INTEGER NOT NULL DEFAULT 10,
    min_graph_lane INTEGER NOT NULL DEFAULT 5,
    require_authority_rerank BOOLEAN NOT NULL DEFAULT TRUE,
    require_numeric_grounding BOOLEAN NOT NULL DEFAULT FALSE,
    require_citation_verification BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qu.retrieval_plan_lanes (
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    lane_name TEXT NOT NULL CHECK (lane_name IN ('alias', 'bm25', 'vector', 'graph', 'rule_lookup', 'numeric_table')),
    lane_priority INTEGER NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    target_k INTEGER NOT NULL,
    hard_filter JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (query_session_id, lane_name)
);

CREATE TABLE IF NOT EXISTS qu.answer_constraints (
    constraint_id TEXT PRIMARY KEY,
    query_type TEXT,
    must_quote_sources BOOLEAN NOT NULL DEFAULT TRUE,
    must_verify_numeric_claims BOOLEAN NOT NULL DEFAULT TRUE,
    must_disclose_conflicts BOOLEAN NOT NULL DEFAULT TRUE,
    forbid_uncited_facts BOOLEAN NOT NULL DEFAULT TRUE,
    forbid_linear_interpolation_without_rule BOOLEAN NOT NULL DEFAULT TRUE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qa.retrieval_runs (
    retrieval_run_id UUID PRIMARY KEY,
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    policy_id TEXT REFERENCES qu.retrieval_policies(policy_id) ON DELETE SET NULL,
    top_k INTEGER NOT NULL,
    fusion_strategy TEXT NOT NULL CHECK (fusion_strategy IN ('rrf', 'weighted_sum', 'manual_priority')),
    rerank_applied BOOLEAN NOT NULL DEFAULT FALSE,
    retrieval_status TEXT NOT NULL DEFAULT 'running' CHECK (retrieval_status IN ('running', 'complete', 'failed')),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS qa.retrieval_lane_hits (
    retrieval_run_id UUID NOT NULL REFERENCES qa.retrieval_runs(retrieval_run_id) ON DELETE CASCADE,
    lane_name TEXT NOT NULL,
    hit_rank INTEGER NOT NULL,
    object_type TEXT NOT NULL CHECK (object_type IN ('document', 'chunk', 'entity', 'fact', 'edge', 'rule')),
    object_id TEXT NOT NULL,
    source_id TEXT,
    score NUMERIC(10,6),
    accepted BOOLEAN NOT NULL DEFAULT TRUE,
    citation_ready BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (retrieval_run_id, lane_name, hit_rank)
);

CREATE INDEX IF NOT EXISTS qa_retrieval_lane_hits_object_idx ON qa.retrieval_lane_hits (object_type, object_id);

CREATE TABLE IF NOT EXISTS qa.evidence_claims (
    evidence_claim_id UUID PRIMARY KEY,
    retrieval_run_id UUID NOT NULL REFERENCES qa.retrieval_runs(retrieval_run_id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    support_object_type TEXT NOT NULL CHECK (support_object_type IN ('document', 'chunk', 'entity', 'fact', 'edge', 'rule')),
    support_object_id TEXT NOT NULL,
    support_strength NUMERIC(5,4),
    citation_required BOOLEAN NOT NULL DEFAULT TRUE,
    numeric_claim BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qa.answer_drafts (
    answer_draft_id UUID PRIMARY KEY,
    query_session_id UUID NOT NULL REFERENCES qu.query_sessions(query_session_id) ON DELETE CASCADE,
    retrieval_run_id UUID REFERENCES qa.retrieval_runs(retrieval_run_id) ON DELETE SET NULL,
    draft_text TEXT NOT NULL,
    model_name TEXT,
    draft_status TEXT NOT NULL DEFAULT 'draft' CHECK (draft_status IN ('draft', 'needs_review', 'verified', 'rejected')),
    unsupported_claim_count INTEGER NOT NULL DEFAULT 0,
    missing_citation_count INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qa.answer_citations (
    answer_draft_id UUID NOT NULL REFERENCES qa.answer_drafts(answer_draft_id) ON DELETE CASCADE,
    citation_order INTEGER NOT NULL,
    cited_object_type TEXT NOT NULL CHECK (cited_object_type IN ('document', 'chunk', 'entity', 'fact', 'edge', 'rule')),
    cited_object_id TEXT NOT NULL,
    citation_span TEXT,
    citation_reason TEXT,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (answer_draft_id, citation_order)
);

CREATE TABLE IF NOT EXISTS qa.citation_verification_runs (
    verification_run_id UUID PRIMARY KEY,
    answer_draft_id UUID NOT NULL REFERENCES qa.answer_drafts(answer_draft_id) ON DELETE CASCADE,
    verifier_model TEXT,
    verification_status TEXT NOT NULL DEFAULT 'running' CHECK (verification_status IN ('running', 'passed', 'failed', 'partial')),
    total_items INTEGER NOT NULL DEFAULT 0,
    passed_items INTEGER NOT NULL DEFAULT 0,
    failed_items INTEGER NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS qa.citation_verification_items (
    verification_run_id UUID NOT NULL REFERENCES qa.citation_verification_runs(verification_run_id) ON DELETE CASCADE,
    citation_order INTEGER NOT NULL,
    verdict TEXT NOT NULL CHECK (verdict IN ('pass', 'fail', 'uncertain')),
    reason TEXT,
    supports_claim BOOLEAN,
    exactness_score NUMERIC(5,4),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (verification_run_id, citation_order)
);

CREATE TABLE IF NOT EXISTS qa.final_answer_audits (
    audit_id UUID PRIMARY KEY,
    answer_draft_id UUID NOT NULL REFERENCES qa.answer_drafts(answer_draft_id) ON DELETE CASCADE,
    release_decision TEXT NOT NULL CHECK (release_decision IN ('approved', 'blocked', 'manual_review')),
    citation_gate_passed BOOLEAN NOT NULL DEFAULT FALSE,
    numeric_gate_passed BOOLEAN NOT NULL DEFAULT FALSE,
    grounding_gate_passed BOOLEAN NOT NULL DEFAULT FALSE,
    rationale TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
