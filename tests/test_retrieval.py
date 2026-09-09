"""Observable retrieval boundaries using synthetic MCP replies."""
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import sqlite3
import unittest
from unittest.mock import patch

from research_skills import retrieval as r
from research_skills.contracts import GateError, validate_evidence


def job(id='q1', **kwargs):
    return {'id': id, 'kind': 'search', 'query': 'retail shopping', 'gap': 'purchase context', **kwargs}


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)

    def init(self, jobs=None, **kwargs):
        return r.initialize(self.work, {'schema_version': 1, 'jobs': jobs or [job()], **kwargs})

    def page(self, text='Retail shopping demand is seasonal.', url='https://example.org/report'):
        self.init([job(kind='extract', url=url)])
        request = r.next_request(self.work)
        r.record(self.work, request['request_id'], {'results': [{'url': url, 'raw_content': text}]})

    def test_tavily_default_dedup_and_reserved_single_call(self):
        self.init([job(), job('q2', query='  RETAIL   shopping ')])
        request = r.next_request(self.work)
        self.assertEqual(request['tool'], 'tavily_search')
        self.assertEqual(request['arguments']['search_depth'], 'basic')
        self.assertEqual(request['arguments']['max_results'], 5)
        with self.assertRaises(GateError):
            r.next_request(self.work)
        self.assertEqual(r.manifest(self.work)['jobs'], 1)

    def test_snippets_and_generated_answer_cannot_be_source_pages(self):
        self.init()
        request = r.next_request(self.work)
        r.record(self.work, request['request_id'], {'answer': 'Fabricated overall conclusion', 'results': [
            {'url': 'https://example.org/report', 'title': 'Report', 'content': 'Search snippet', 'raw_content': 'Not requested'}]})
        self.assertEqual(r.ledger(self.work)['documents'], [])
        self.assertEqual(r.search_local(self.work, 'snippet'), [])
        self.assertNotIn('Fabricated', json.dumps(r.status(self.work)))

    def test_page_offsets_hashes_and_unreviewed_ledger(self):
        text = 'Introduction.\n' + '消费者购物场景 seasonal shopping demand. ' * 100
        self.page(text)
        ledger = r.ledger(self.work)
        self.assertEqual(ledger['documents'][0]['text'], text)
        with self.assertRaises(GateError):
            validate_evidence(ledger)
        hit = r.search_local(self.work, '购物场景 seasonal')[0]
        self.assertEqual(hit['quote'], text[hit['start']:hit['end']])
        self.assertFalse(hit['semantic_reviewed'])

    def test_restart_does_not_reissue_and_replay_is_bound(self):
        self.init()
        request = r.next_request(self.work)
        reply = {'results': []}
        r.record(self.work, request['request_id'], reply)
        self.assertIsNone(r.next_request(self.work))
        with self.assertRaises(GateError):
            r.record(self.work, request['request_id'], reply)
        self.assertEqual(r.manifest(self.work)['issued_calls'], 1)

    def test_cross_workspace_request_rejected(self):
        self.init()
        request = r.next_request(self.work)
        other = self.work / 'other'
        r.initialize(other, {'schema_version': 1, 'jobs': [job()]})
        r.next_request(other)
        with self.assertRaises(GateError):
            r.record(other, request['request_id'], {'results': []})

    def test_rate_limit_backoff_and_attempt_cap(self):
        self.init(max_attempts=2)
        with patch.object(r.time, 'time', return_value=100):
            request = r.next_request(self.work)
            r.fail(self.work, request['request_id'], '429')
            with self.assertRaises(GateError):
                r.next_request(self.work)
        with patch.object(r.time, 'time', return_value=102):
            request = r.next_request(self.work)
            r.fail(self.work, request['request_id'], '429')
            self.assertIsNone(r.next_request(self.work))
        self.assertEqual(r.manifest(self.work)['failed_jobs'], 1)

    def test_global_call_budget_survives_restart(self):
        self.init([job(), job('q2', query='different question')], max_calls=1)
        request = r.next_request(self.work)
        r.record(self.work, request['request_id'], {'results': []})
        with self.assertRaises(GateError):
            r.next_request(self.work)

    def test_firecrawl_is_explicit_extract_and_markdown_only(self):
        self.init([job(kind='extract', provider='firecrawl', url='https://example.org/report')])
        request = r.next_request(self.work)
        self.assertEqual(request['tool'], 'firecrawl_scrape')
        self.assertEqual(request['arguments']['formats'], ['markdown'])
        r.record(self.work, request['request_id'], {'success': True, 'data': {
            'markdown': 'Retail source page', 'metadata': {'sourceURL': 'https://example.org/report'}}})
        self.assertEqual(len(r.ledger(self.work)['documents']), 1)

    def test_wrong_url_and_mcp_error_leave_request_unresolved(self):
        self.init([job(kind='extract', url='https://example.org/right')])
        request = r.next_request(self.work)
        for reply in [{'results': [{'url': 'https://example.org/wrong', 'raw_content': 'wrong'}]},
                      {'isError': True, 'content': [{'type': 'text', 'text': 'failed'}]}]:
            with self.assertRaises(GateError):
                r.record(self.work, request['request_id'], reply)
        self.assertEqual(r.manifest(self.work)['source_pages'], 0)
        self.assertEqual(r.manifest(self.work)['inflight_jobs'], 1)

    def test_mcp_text_envelope_and_url_tracking_dedup(self):
        self.init()
        request = r.next_request(self.work)
        data = {'results': [{'url': 'https://EXAMPLE.org/report?utm_source=x#top', 'content': 'one'},
                            {'url': 'https://example.org/report', 'content': 'two'}]}
        r.record(self.work, request['request_id'], {'content': [{'type': 'text', 'text': json.dumps(data)}]})
        self.assertEqual(r.manifest(self.work)['unique_urls'], 1)

    def test_source_versions_remain_separate(self):
        self.page('Old source text.')
        r.add(self.work, job('update', kind='extract', provider='firecrawl', url='https://example.org/report'))
        request = r.next_request(self.work)
        r.record(self.work, request['request_id'], {'markdown': 'New source text.', 'metadata': {'sourceURL': 'https://example.org/report'}})
        docs = r.ledger(self.work)['documents']
        self.assertEqual(len(docs), 2)
        self.assertNotEqual(docs[0]['id'], docs[1]['id'])

    def test_manifest_has_no_query_url_text_or_response(self):
        self.page('CONFIDENTIAL-SYNTHETIC retail source')
        result = json.dumps(r.manifest(self.work))
        for value in ['CONFIDENTIAL', 'example.org', 'purchase context', 'raw_content']:
            self.assertNotIn(value, result)
        self.assertFalse(r.manifest(self.work)['research_verified'])

    def test_invalid_plan_preserves_previous_state(self):
        self.init()
        before = r.manifest(self.work)
        with self.assertRaises(GateError):
            r.add(self.work, job('unsafe', kind='extract', url='file:///private/document'))
        self.assertEqual(before, r.manifest(self.work))
        with self.assertRaises(GateError):
            self.init()

    def test_explicit_gap_required_and_auth_error_does_not_fallback(self):
        self.init()
        with self.assertRaises(GateError):
            r.add(self.work, job('q2', gap=''))
        request = r.next_request(self.work)
        r.fail(self.work, request['request_id'], '401')
        self.assertIsNone(r.next_request(self.work))
        self.assertEqual(r.manifest(self.work)['issued_calls'], 1)

    def test_failed_extract_is_not_empty_success(self):
        self.init([job(kind='extract', url='https://example.org/report')])
        request = r.next_request(self.work)
        with self.assertRaises(GateError):
            r.record(self.work, request['request_id'], {'results': [], 'failed_results': [{'url': 'https://example.org/report'}]})
        self.assertEqual(r.manifest(self.work)['empty_jobs'], 0)

    def test_malformed_second_result_rolls_back_whole_import(self):
        self.init()
        request = r.next_request(self.work)
        with self.assertRaises(GateError):
            r.record(self.work, request['request_id'], {'results': [
                {'url': 'https://example.org/report', 'content': 'valid snippet'}, {'url': 'file:///bad'}]})
        self.assertEqual(r.manifest(self.work)['search_snippets'], 0)

    def test_source_hash_tampering_refuses_candidate_export(self):
        self.page()
        with sqlite3.connect(self.work / '.retrieval/state.sqlite3') as connection:
            state = json.loads(connection.execute('SELECT payload FROM journal').fetchone()[0])
            next(iter(state['documents'].values()))['text'] = 'tampered'
            connection.execute('UPDATE journal SET payload=?', (json.dumps(state),))
        with self.assertRaises(GateError):
            r.ledger(self.work)

    def test_dedup_retains_other_evidence_gaps(self):
        self.init([job(), job('q2', gap='another decision')])
        self.assertEqual(r.status(self.work)['jobs'][0]['related_gaps'], ['another decision'])

    def test_actual_cli_resumption_and_no_overwrite(self):
        self.page()
        def run(*args):
            return subprocess.run([sys.executable, '-m', 'research_skills', *args], capture_output=True, text=True)
        result = run('retrieval-manifest', '--workspace', str(self.work))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['source_pages'], 1)
        output = self.work / 'evidence.json'
        args = ('retrieval-ledger', '--workspace', str(self.work), '--output', str(output))
        self.assertEqual(run(*args).returncode, 0)
        before = output.read_bytes()
        self.assertEqual(run(*args).returncode, 2)
        self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
