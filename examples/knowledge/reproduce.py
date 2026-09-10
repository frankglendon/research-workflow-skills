"""Build and query an original public demo corpus without network or model calls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from research_skills import knowledge

ROWS = [
    ('method-price', 'Comparable price samples', 'method', 'price_tiers', '价格 定价 比价 pricing price SKU', 6),
    ('method-country', 'Country comparison', 'method', 'country_comparison', '国别 国家 本地化 country', 9),
    ('method-competitor', 'Competitive mechanism', 'method', 'competitor_actions', '竞品 对手 competitor competition', 12),
    ('method-opportunity', 'Opportunity judgment', 'method', 'opportunity', '机会 优先级 opportunity priority', 15),
    ('template-price', 'Price comparison page', 'template', 'price_tiers', '价格 价位 pricing price', 18),
    ('template-country', 'Country comparison page', 'template', 'country_comparison', '国别 国家 country', 21),
    ('template-competitor', 'Competitive action page', 'template', 'competitor_actions', '竞品 行动 competitor', 24),
    ('template-opportunity', 'Opportunity page', 'template', 'opportunity', '机会 矩阵 opportunity', 27),
]


def run(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    source = Path(__file__).with_name('methods.md')
    lines = source.read_text(encoding='utf-8').splitlines()
    cards = [{'id': cid, 'title': title, 'kind': kind, 'page_type': page_type,
              'tags': tags.split(), 'stage': 'analysis' if kind == 'method' else 'design',
              'visibility': 'public', 'review_status': 'reviewed', 'body': lines[line-1],
              'cautions': ['A reference recipe is not current market evidence.'],
              'sources': [{'source_id': 'original-demo', 'lines': [line, line]}]}
             for cid, title, kind, page_type, tags, line in ROWS]
    catalog = {'schema_version': 1, 'sources': [{'id': 'original-demo',
        'path': os.path.relpath(source, output), 'visibility': 'public',
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}], 'cards': cards}
    (output/'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding='utf-8')
    build = knowledge.build(output/'catalog.json', output/'index.sqlite3')
    query = 'Comparable price samples and pricing table'
    context = knowledge.context(output/'index.sqlite3', query, audience='external', limit=2)
    checks = []
    for query, expected in [('商品价格比较', 'method-price'), ('国家本地化差异', 'method-country'),
                            ('competitor purchase task', 'method-competitor'), ('机会优先级', 'method-opportunity')]:
        hits = knowledge.search(output/'index.sqlite3', query, kind='method', audience='external', limit=1)['hits']
        checks.append({'query': query, 'expected_top1': expected, 'actual_top1': hits[0]['id'] if hits else None})
    report = {'build': build, 'checks': checks,
              'passed': all(c['actual_top1'] == c['expected_top1'] for c in checks),
              'scope': 'Small authored retrieval smoke set; not a research-quality evaluation.'}
    for name, value in [('context.json', context), ('retrieval-checks.json', report)]:
        (output/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    result = run(parser.parse_args().output)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)
