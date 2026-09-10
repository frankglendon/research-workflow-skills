import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

from research_skills.cli import main


class KnowledgeCliTests(unittest.TestCase):
    def test_public_demo_and_cli_source_status(self):
        path = Path(__file__).resolve().parents[1] / 'examples/knowledge/reproduce.py'
        spec = importlib.util.spec_from_file_location('knowledge_demo', path)
        demo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(demo)
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'demo'
            report = demo.run(output)
            self.assertTrue(report['passed'])
            self.assertEqual(report['build']['indexed_cards'], 8)
            for command, args in [('kb-status', []), ('kb-search', ['--query', '价格']),
                                  ('kb-context', ['--query', '价格', '--audience', 'external'])]:
                stream = io.StringIO()
                with contextlib.redirect_stdout(stream):
                    self.assertEqual(main([command, '--index', str(output/'index.sqlite3'), *args]), 0)
                result = json.loads(stream.getvalue())
                self.assertNotIn('stale', result.get('status', ''))
                if command == 'kb-context':
                    self.assertTrue(result['external_model_allowed'])
                    self.assertNotIn(str(path.parent), stream.getvalue())
                    self.assertEqual(result['hits'][0]['id'], 'method-price')

    def test_missing_index_is_a_blocked_cli_result(self):
        with tempfile.TemporaryDirectory() as temp:
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = main(['kb-status', '--index', str(Path(temp)/'absent.sqlite3')])
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(stream.getvalue())['status'], 'blocked')
