#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / 'docs/tier0/postgres-dict-bundle'
DATA_DIR = OUT_DIR / 'data'
MANIFEST = OUT_DIR / 'manifest.json'
IMPORT_SQL = OUT_DIR / 'import.sql'

TERM_MAP = ROOT / 'docs/tier0/bilingual-term-map.json'
ALIAS_REGISTRY = ROOT / 'docs/tier0/alias-registry.jsonl'
BUILD_ARCHETYPES = ROOT / 'docs/tier0/build-archetypes.jsonl'
STRUCTURED = ROOT / 'docs/tier0/structured'


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.open(encoding='utf-8') if line.strip()]


def slugify(text: str) -> str:
    return ''.join(ch.lower() if ch.isalnum() else '-' for ch in text).strip('-') or 'unknown'


def stable_id(prefix: str, *parts: str) -> str:
    raw = '||'.join(parts)
    digest = hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]
    return f'{prefix}::{digest}'


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def write_tsv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.writer(handle, delimiter='\t', quotechar='"', lineterminator='\n')
        for row in rows:
            writer.writerow(['\\N' if row.get(col) is None else row.get(col) for col in columns])


def build_terms_and_aliases() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    term_map = load_json(TERM_MAP)
    alias_rows_from_registry = load_jsonl(ALIAS_REGISTRY)

    term_rows: list[dict[str, Any]] = []
    alias_rows: list[dict[str, Any]] = []
    term_id_by_canonical: dict[str, str] = {}

    for query_term, payload in sorted(term_map.items(), key=lambda item: item[0].lower()):
        canonical = str(payload.get('canonical_hint') or query_term).strip()
        term_id = stable_id('term', canonical)
        term_id_by_canonical[canonical.lower()] = term_id
        aliases = [str(alias).strip() for alias in payload.get('aliases', []) if str(alias).strip()]
        zh_name = canonical if any('\u4e00' <= ch <= '\u9fff' for ch in canonical) else None
        domain = 'query_understanding'
        term_type = 'community_term' if query_term != canonical else 'canonical_term'
        term_rows.append({
            'term_id': term_id,
            'canonical_term': canonical,
            'canonical_term_zh': zh_name,
            'term_type': term_type,
            'domain': domain,
            'language': 'mixed',
            'description': f'Query rewrite anchor for {query_term}',
            'source': 'docs/tier0/bilingual-term-map.json',
            'confidence': 0.99,
            'active': True,
            'metadata': dump_json({
                'query_term': query_term,
                'preferred_title_contains': payload.get('preferred_title_contains', []),
                'preferred_text_contains': payload.get('preferred_text_contains', []),
                'preferred_source_ids': payload.get('preferred_source_ids', []),
                'discouraged_source_ids': payload.get('discouraged_source_ids', []),
            }),
        })
        alias_rows.append({
            'alias_id': stable_id('alias', query_term, canonical, 'key'),
            'term_id': term_id,
            'canonical_term': canonical,
            'alias': query_term,
            'alias_class': 'query_term_key',
            'language': 'mixed',
            'community_frequency': None,
            'confidence': 0.99,
            'source': 'docs/tier0/bilingual-term-map.json',
            'active': True,
            'rewrite_priority': 10,
            'metadata': dump_json({'origin': 'term_map_key'}),
        })
        for alias in aliases:
            alias_rows.append({
                'alias_id': stable_id('alias', alias, canonical, 'map'),
                'term_id': term_id,
                'canonical_term': canonical,
                'alias': alias,
                'alias_class': 'canonical_expansion',
                'language': 'zh' if any('\u4e00' <= ch <= '\u9fff' for ch in alias) else 'en',
                'community_frequency': None,
                'confidence': 0.95,
                'source': 'docs/tier0/bilingual-term-map.json',
                'active': True,
                'rewrite_priority': 20,
                'metadata': dump_json({'origin': 'term_map_alias'}),
            })

    for row in alias_rows_from_registry:
        canonical = str(row.get('canonical_name') or row.get('canonical_id')).strip()
        term_id = term_id_by_canonical.get(canonical.lower())
        if not term_id:
            term_id = stable_id('term', canonical)
            term_id_by_canonical[canonical.lower()] = term_id
            term_rows.append({
                'term_id': term_id,
                'canonical_term': canonical,
                'canonical_term_zh': canonical if any('\u4e00' <= ch <= '\u9fff' for ch in canonical) else None,
                'term_type': 'canonical_term',
                'domain': 'community_alias',
                'language': row.get('language') or 'mixed',
                'description': f'Alias anchor for {canonical}',
                'source': row.get('source'),
                'confidence': row.get('confidence') or 0.95,
                'active': True,
                'metadata': dump_json({'canonical_id': row.get('canonical_id')}),
            })
        alias_rows.append({
            'alias_id': row['alias_id'],
            'term_id': term_id,
            'canonical_term': canonical,
            'alias': row['alias'],
            'alias_class': row.get('alias_type') or 'alias',
            'language': row.get('language'),
            'community_frequency': None,
            'confidence': row.get('confidence'),
            'source': row.get('source'),
            'active': True,
            'rewrite_priority': 50,
            'metadata': dump_json({'origin': 'alias_registry'}),
        })

    # dedup
    dedup_terms = {row['term_id']: row for row in term_rows}
    dedup_aliases = {(row['canonical_term'], row['alias'], row['alias_class']): row for row in alias_rows}

    return {
        'term_dictionary': (list(dedup_terms.values()), ['term_id','canonical_term','canonical_term_zh','term_type','domain','language','description','source','confidence','active','metadata']),
        'alias_dictionary': (list(dedup_aliases.values()), ['alias_id','term_id','canonical_term','alias','alias_class','language','community_frequency','confidence','source','active','rewrite_priority','metadata']),
    }


def build_build_dict() -> dict[str, tuple[list[dict[str, Any]], list[str]]]:
    builds = load_jsonl(BUILD_ARCHETYPES)
    build_rows=[]
    skill_rows=[]
    for row in builds:
        build_rows.append({
            'build_id': row['build_id'],
            'class_name': row.get('class'),
            'build_name': row['canonical_name'],
            'build_name_zh': row['title'].split(' / ')[1].replace('（Curated Anchor Card）','') if ' / ' in row.get('title','') else None,
            'aliases': dump_json(row.get('aliases', [])),
            'source': row.get('source'),
            'confidence': 0.95,
            'active': True,
            'metadata': dump_json({'source_id': row.get('source_id'), 'title': row.get('title')}),
        })
        for idx, skill in enumerate(row.get('core_skills', []), start=1):
            skill_rows.append({'build_id': row['build_id'], 'skill_order': idx, 'skill_name': skill})
    return {
        'build_dictionary': (build_rows, ['build_id','class_name','build_name','build_name_zh','aliases','source','confidence','active','metadata']),
        'build_dictionary_skills': (skill_rows, ['build_id','skill_order','skill_name']),
    }


def build_item_dict() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[]
    for path, family, rarity in [
        (STRUCTURED / 'base-items.jsonl', 'base_item', None),
        (STRUCTURED / 'runes.jsonl', 'rune', 'rune'),
        (STRUCTURED / 'runewords.jsonl', 'runeword', 'runeword'),
        (STRUCTURED / 'unique-items.jsonl', 'unique_item', 'unique'),
    ]:
        for row in load_jsonl(path):
            item_id = row.get('item_id') or row.get('rune_id') or row.get('runeword_id') or row.get('unique_item_id')
            name = row.get('name') or row.get('canonical_name')
            name_zh = row.get('name_zh')
            keywords = [name]
            if name_zh:
                keywords.append(name_zh)
            if family == 'base_item':
                keywords.extend(filter(None, [row.get('bucket'), row.get('item_type'), row.get('item_type_2')]))
            elif family == 'runeword':
                keywords.extend(row.get('allowed_item_types', []))
            rows.append({
                'item_id': item_id,
                'canonical_name': name,
                'canonical_name_zh': name_zh,
                'item_family': family,
                'rarity': rarity,
                'base_code': row.get('base_code') or row.get('code'),
                'normalized_keywords': dump_json(sorted({k for k in keywords if k})),
                'source': row.get('source'),
                'active': True,
                'metadata': dump_json({'source_file': row.get('source_file')}),
            })
    return rows, ['item_id','canonical_name','canonical_name_zh','item_family','rarity','base_code','normalized_keywords','source','active','metadata']


def build_area_dict() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[]
    for row in load_jsonl(STRUCTURED / 'areas.jsonl'):
        area_tags=[]
        if row.get('is_inside'):
            area_tags.append('indoor')
        else:
            area_tags.append('outdoor')
        if row.get('waypoint') not in (None, 255):
            area_tags.append('waypoint')
        farm_tags=[]
        if (row.get('level_hell') or 0) >= 85:
            farm_tags.append('lvl85')
        rows.append({
            'area_id': row['area_id'],
            'canonical_name': row['name'],
            'canonical_name_zh': row.get('name_zh'),
            'act': row.get('act'),
            'area_tags': dump_json(area_tags),
            'farm_tags': dump_json(farm_tags),
            'source': row.get('source'),
            'active': True,
            'metadata': dump_json({'level_hell': row.get('level_hell'), 'monster_density_hell': row.get('monster_density_hell')}),
        })
    return rows, ['area_id','canonical_name','canonical_name_zh','act','area_tags','farm_tags','source','active','metadata']


def build_monster_dict() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[]
    for row in load_jsonl(STRUCTURED / 'monster-resistances.jsonl'):
        tags=[]
        if row.get('monster_type'):
            tags.append(str(row['monster_type']))
        resistances=row.get('resistances', {})
        for rtype, values in resistances.items():
            hell=values.get('hell')
            if hell is not None and hell >= 100:
                tags.append(f'hell_immune_{rtype}')
        rows.append({
            'monster_id': row['monster_id'],
            'canonical_name': row['name'],
            'canonical_name_zh': row.get('name_zh'),
            'monster_type': row.get('monster_type'),
            'monster_tags': dump_json(sorted(set(tags))),
            'source': row.get('source'),
            'active': True,
            'metadata': dump_json({'base_id': row.get('base_id'), 'source_file': row.get('source_file')}),
        })
    return rows, ['monster_id','canonical_name','canonical_name_zh','monster_type','monster_tags','source','active','metadata']


def build_rule_dict() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[]
    for row in load_jsonl(STRUCTURED / 'breakpoints.jsonl'):
        rows.append({
            'rule_id': stable_id('rule', 'breakpoint', row['category'], row['entity']),
            'rule_type': 'breakpoint_table',
            'subject_type': row['category'],
            'canonical_subject': row['entity'],
            'description': f"{row['entity']} {row['category']} breakpoint table",
            'rule_jsonb': dump_json({'breakpoints': row['breakpoints']}),
            'source': row.get('source_url') or row.get('source'),
            'confidence': 0.95,
            'active': True,
            'metadata': dump_json({'source_file': 'breakpoints.jsonl'}),
        })
    for row in load_jsonl(STRUCTURED / 'cube-recipes.jsonl')[:250]:
        rows.append({
            'rule_id': row['recipe_id'],
            'rule_type': 'cube_recipe',
            'subject_type': row.get('recipe_type'),
            'canonical_subject': row['description'],
            'description': row['description'],
            'rule_jsonb': dump_json({'inputs': row.get('inputs', []), 'output': row.get('output'), 'modifiers': row.get('modifiers', {})}),
            'source': row.get('source'),
            'confidence': 0.9,
            'active': True,
            'metadata': dump_json({'source_file': row.get('source_file')}),
        })
    return rows, ['rule_id','rule_type','subject_type','canonical_subject','description','rule_jsonb','source','confidence','active','metadata']


def build_query_patterns() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[
        {
            'pattern_id': 'pattern::community_alias_fact',
            'query_type': 'fact_lookup',
            'trigger_phrase': '是什么 掉不掉 在哪',
            'intent_label': 'community_alias_resolution',
            'expansion_policy': 'alias_then_canonical_then_source_bias',
            'requires_subquestions': False,
            'requires_numeric_guard': False,
            'requires_citation_verification': True,
            'lane_hints': dump_json(['alias','bm25','graph']),
            'source': 'schema_seed',
            'active': True,
            'metadata': dump_json({'examples': ['劳模掉不掉军帽', 'SOJ是什么']}),
        },
        {
            'pattern_id': 'pattern::numeric_breakpoint',
            'query_type': 'numeric_reasoning',
            'trigger_phrase': 'FCR FHR FBR 档位 是否到下一个档',
            'intent_label': 'breakpoint_lookup',
            'expansion_policy': 'entity_plus_numeric_table',
            'requires_subquestions': True,
            'requires_numeric_guard': True,
            'requires_citation_verification': True,
            'lane_hints': dump_json(['alias','rule_lookup','numeric_table','graph']),
            'source': 'schema_seed',
            'active': True,
            'metadata': dump_json({'examples': ['90 FCR 带精神盾能否上档']}),
        },
        {
            'pattern_id': 'pattern::build_route_multihop',
            'query_type': 'multi_hop_strategy',
            'trigger_phrase': '怎么刷 最高效 核心装备 底材 去哪里',
            'intent_label': 'build_to_farm_route',
            'expansion_policy': 'build_entity_to_graph_expansion',
            'requires_subquestions': True,
            'requires_numeric_guard': False,
            'requires_citation_verification': True,
            'lane_hints': dump_json(['alias','graph','bm25','vector']),
            'source': 'schema_seed',
            'active': True,
            'metadata': dump_json({'examples': ['锤丁谜团底材去哪里刷最高效']}),
        },
    ]
    return rows, ['pattern_id','query_type','trigger_phrase','intent_label','expansion_policy','requires_subquestions','requires_numeric_guard','requires_citation_verification','lane_hints','source','active','metadata']


def build_retrieval_policies() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[
        {
            'policy_id':'policy::default_fact',
            'policy_name':'Default Fact Policy',
            'query_type':'fact_lookup',
            'min_alias_lane':8,
            'min_bm25_lane':12,
            'min_vector_lane':8,
            'min_graph_lane':4,
            'require_authority_rerank':True,
            'require_numeric_grounding':False,
            'require_citation_verification':True,
            'metadata':dump_json({'fusion_strategy':'rrf'})
        },
        {
            'policy_id':'policy::numeric_guarded',
            'policy_name':'Numeric Guarded Policy',
            'query_type':'numeric_reasoning',
            'min_alias_lane':6,
            'min_bm25_lane':10,
            'min_vector_lane':6,
            'min_graph_lane':6,
            'require_authority_rerank':True,
            'require_numeric_grounding':True,
            'require_citation_verification':True,
            'metadata':dump_json({'fusion_strategy':'weighted_sum'})
        },
        {
            'policy_id':'policy::multi_hop_build',
            'policy_name':'Multi-hop Build Policy',
            'query_type':'multi_hop_strategy',
            'min_alias_lane':6,
            'min_bm25_lane':10,
            'min_vector_lane':10,
            'min_graph_lane':8,
            'require_authority_rerank':True,
            'require_numeric_grounding':False,
            'require_citation_verification':True,
            'metadata':dump_json({'fusion_strategy':'rrf'})
        },
    ]
    return rows, ['policy_id','policy_name','query_type','min_alias_lane','min_bm25_lane','min_vector_lane','min_graph_lane','require_authority_rerank','require_numeric_grounding','require_citation_verification','metadata']


def build_answer_constraints() -> tuple[list[dict[str, Any]], list[str]]:
    rows=[
        {
            'constraint_id':'constraint::strict_default',
            'query_type':'default',
            'must_quote_sources':True,
            'must_verify_numeric_claims':True,
            'must_disclose_conflicts':True,
            'forbid_uncited_facts':True,
            'forbid_linear_interpolation_without_rule':True,
            'metadata':dump_json({'release_gate':'strict'})
        },
        {
            'constraint_id':'constraint::numeric_table',
            'query_type':'numeric_reasoning',
            'must_quote_sources':True,
            'must_verify_numeric_claims':True,
            'must_disclose_conflicts':True,
            'forbid_uncited_facts':True,
            'forbid_linear_interpolation_without_rule':True,
            'metadata':dump_json({'require_table_lookup':True})
        },
    ]
    return rows, ['constraint_id','query_type','must_quote_sources','must_verify_numeric_claims','must_disclose_conflicts','forbid_uncited_facts','forbid_linear_interpolation_without_rule','metadata']


def build_import_sql(table_specs: dict[str, tuple[list[dict[str, Any]], list[str]]]) -> str:
    order=[
        'term_dictionary','alias_dictionary','build_dictionary','build_dictionary_skills','item_dictionary','area_dictionary','monster_dictionary','rule_dictionary','query_pattern_dictionary','retrieval_policies','answer_constraints'
    ]
    trunc=list(reversed(order))
    lines=['\\set ON_ERROR_STOP on','BEGIN;']
    mapping={
        'term_dictionary':'dict.term_dictionary',
        'alias_dictionary':'dict.alias_dictionary',
        'build_dictionary':'dict.build_dictionary',
        'build_dictionary_skills':'dict.build_dictionary_skills',
        'item_dictionary':'dict.item_dictionary',
        'area_dictionary':'dict.area_dictionary',
        'monster_dictionary':'dict.monster_dictionary',
        'rule_dictionary':'dict.rule_dictionary',
        'query_pattern_dictionary':'dict.query_pattern_dictionary',
        'retrieval_policies':'qu.retrieval_policies',
        'answer_constraints':'qu.answer_constraints',
    }
    for t in trunc:
        lines.append(f'TRUNCATE TABLE {mapping[t]} CASCADE;')
    for t in order:
        _, cols = table_specs[t]
        path=(DATA_DIR / f'{t}.tsv').resolve()
        lines.append(f"\\copy {mapping[t]} ({', '.join(cols)}) FROM '{path}' WITH (FORMAT csv, DELIMITER E'\\t', QUOTE '\"', NULL '\\N')")
    lines.append('COMMIT;')
    return '\n'.join(lines)+'\n'


def main() -> int:
    table_specs={}
    table_specs.update(build_terms_and_aliases())
    table_specs.update(build_build_dict())
    table_specs['item_dictionary']=build_item_dict()
    table_specs['area_dictionary']=build_area_dict()
    table_specs['monster_dictionary']=build_monster_dict()
    table_specs['rule_dictionary']=build_rule_dict()
    table_specs['query_pattern_dictionary']=build_query_patterns()
    table_specs['retrieval_policies']=build_retrieval_policies()
    table_specs['answer_constraints']=build_answer_constraints()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest_tables={}
    for table_name, (rows, columns) in table_specs.items():
        write_tsv(DATA_DIR / f'{table_name}.tsv', rows, columns)
        manifest_tables[table_name] = {
            'rows': len(rows),
            'columns': columns,
            'path': str((DATA_DIR / f'{table_name}.tsv').relative_to(ROOT)),
        }
    IMPORT_SQL.write_text(build_import_sql(table_specs), encoding='utf-8')
    manifest = {
        'schema_files': [
            'sql/postgres/004_dict_query_quality_schema.sql',
            'sql/postgres/005_dict_query_quality_views.sql',
            'sql/postgres/query_understanding_queries.sql',
        ],
        'tables': manifest_tables,
        'import_sql': str(IMPORT_SQL.relative_to(ROOT)),
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v['rows'] for k,v in manifest_tables.items()}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
