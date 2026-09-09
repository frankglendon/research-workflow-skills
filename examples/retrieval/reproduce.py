"""Replay synthetic MCP responses through the retrieval module; no network or models."""
import argparse
import json
from pathlib import Path
from research_skills import retrieval
from research_skills.contracts import GateError, validate_evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    output = Path(parser.parse_args().output)
    output.mkdir(parents=True, exist_ok=False)
    plan = {'schema_version': 1, 'max_calls': 3, 'jobs': [
        {'id': 'q1', 'kind': 'search', 'query': 'fictional retail gifting study', 'gap': 'Find a candidate source'},
        {'id': 'page1', 'kind': 'extract', 'url': 'https://example.org/retail', 'gap': 'Read the page, not the snippet'},
        {'id': 'page2', 'kind': 'extract', 'provider': 'firecrawl', 'url': 'https://example.org/methods', 'gap': 'Demonstrate the explicit alternative adapter'}]}
    responses = [
        {'answer': 'This generated answer must not enter the source corpus.', 'results': [
            {'url': 'https://example.org/retail', 'title': 'Fictional study', 'content': 'Synthetic discovery snippet'}]},
        {'results': [{'url': 'https://example.org/retail', 'title': 'Fictional retail page',
                      'raw_content': 'Synthetic source fixture. Gift shopping depends on occasion and recipient. No consumer findings are reported.'}]},
        {'success': True, 'data': {'markdown': 'Synthetic methods fixture. Separate gift shopping assumptions from measured consumer findings.',
                                  'metadata': {'sourceURL': 'https://example.org/methods', 'title': 'Fictional methods page'}}}]
    retrieval.initialize(output, plan)
    for response in responses:
        request = retrieval.next_request(output)
        retrieval.record(output, request['request_id'], response)
    assert retrieval.next_request(output) is None
    ledger = retrieval.ledger(output)
    candidates = retrieval.search_local(output, 'gift shopping', top_k=3)
    assert candidates and len(ledger['documents']) == 2
    blocked = False
    try:
        validate_evidence(ledger)
    except GateError:
        blocked = True
    assert blocked, 'Unreviewed sources must not become a final evidence report'
    result = {**retrieval.manifest(output), 'synthetic': True, 'network_calls': 0,
              'unreviewed_ledger_blocked': blocked, 'candidate_chunks': len(candidates)}
    for name, data in [('plan.json', plan), ('source-candidates.json', ledger),
                       ('local-candidates.json', candidates), ('manifest.json', result)]:
        (output / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
