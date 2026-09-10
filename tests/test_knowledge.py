import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from research_skills import knowledge as kb
from research_skills.contracts import GateError


class KnowledgeTests(unittest.TestCase):
    def test_status_detects_source_change_without_mutating_index(self):
        self.build()
        original = self.index.read_bytes()
        self.assertEqual(kb.status(self.index)['status'], 'current')
        self.source.write_text('Changed source')
        self.assertEqual(kb.status(self.index)['stale_cards'], ['price'])
        self.assertEqual(self.index.read_bytes(), original)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'methods.md'
        self.source.write_text('# Methods\n价格比较保留币种、规格、起价与促销日期。\nOther guidance.\n')
        self.index = self.root / 'index.sqlite3'

    def catalog(self, visibility='local_only'):
        return {'schema_version': 1, 'sources': [{'id': 'source', 'path': 'methods.md',
            'visibility': visibility, 'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}],
            'cards': [{'id': 'price', 'title': '可比价格阶梯', 'kind': 'method', 'stage': 'analysis',
                'page_type': 'price_tiers', 'tags': ['pricing', '价格', '币种'], 'visibility': visibility,
                'review_status': 'reviewed', 'body': '按商品规格、币种、日期比较价格；起价不是均价。',
                'cautions': ['旧价格不是当前市场证据。'],
                'sources': [{'source_id': 'source', 'lines': [2, 2]}]}]}

    def build(self, data=None):
        p=self.root/'catalog.json';p.write_text(json.dumps(data or self.catalog(),ensure_ascii=False))
        return kb.build(p, self.index)

    def test_chinese_and_english_retrieval_preserve_provenance(self):
        self.build()
        for query in ['商品价格比较', 'pricing ladder']:
            hit=kb.search(self.index, query)['hits'][0]
            self.assertEqual(hit['id'], 'price')
            self.assertEqual(hit['sources'][0]['lines'], [2, 2])
            self.assertEqual(hit['sources'][0]['quote'], '价格比较保留币种、规格、起价与促销日期。')
            self.assertFalse(hit['usable_as_current_market_evidence'])

    def test_local_material_is_excluded_from_external_context(self):
        self.build()
        result=kb.context(self.index, '价格', audience='external')
        self.assertEqual(result['hits'], [])
        self.assertNotIn(str(self.root), json.dumps(result))
        local=kb.context(self.index, '价格')
        self.assertEqual(local['classification'], 'local_only')
        self.assertFalse(local['external_model_allowed'])

    def test_public_search_omits_local_paths(self):
        self.build(self.catalog('public'))
        result=kb.context(self.index, '价格', audience='external')
        self.assertTrue(result['external_model_allowed'])
        self.assertEqual(len(result['hits']), 1)
        self.assertNotIn(str(self.root), json.dumps(result))

    def test_public_card_cannot_relabel_private_source(self):
        data=self.catalog();data['cards'][0]['visibility']='public'
        with self.assertRaises(GateError):self.build(data)

    def test_source_change_or_deletion_suppresses_stale_guidance(self):
        self.build();self.source.write_text('changed')
        result=kb.search(self.index, '价格')
        self.assertEqual(result['hits'], [])
        self.assertTrue(result['stale_cards'])
        self.source.unlink()
        self.assertEqual(kb.search(self.index, '价格')['hits'], [])

    def test_failed_rebuild_preserves_previous_index(self):
        self.build();before=self.index.read_bytes()
        data=self.catalog();data['sources'][0]['sha256']='0'*64
        with self.assertRaises(GateError):self.build(data)
        self.assertEqual(before,self.index.read_bytes())

    def test_unreviewed_cards_are_not_searchable(self):
        data=self.catalog();data['cards'][0]['review_status']='quarantined'
        result=self.build(data)
        self.assertEqual(result['indexed_cards'],0)
        self.assertEqual(kb.search(self.index,'价格')['hits'],[])

    def test_source_type_and_line_ranges_are_validated(self):
        data=self.catalog();data['cards'][0]['sources'][0]['lines']=[2,200]
        with self.assertRaises(GateError):self.build(data)
        data=self.catalog();data['sources'][0]['path']='secret.env'
        (self.root/'secret.env').write_text('not a research source')
        with self.assertRaises(GateError):self.build(data)

    def test_context_budget_never_truncates_a_card_or_loses_its_citation(self):
        self.build()
        full=kb.context(self.index,'价格',max_chars=8000)
        self.assertEqual(len(full['hits']),1)
        short=kb.context(self.index,'价格',max_chars=20)
        self.assertEqual(short['hits'],[])
        self.assertTrue(short['budget_omitted'])
        self.assertIn('reference_material',full['role'])

    def test_query_is_not_sql_and_filters_work(self):
        self.build()
        self.assertEqual(kb.search(self.index,'价格',kind='template')['hits'],[])
        kb.search(self.index,'价格 "); DROP TABLE cards; --')
        self.assertEqual(kb.search(self.index,'价格')['hits'][0]['id'],'price')
        self.assertEqual(kb.search(self.index,'!!!')['hits'],[])

    def test_duplicate_card_ids_block_build(self):
        data=self.catalog();data['cards'].append(dict(data['cards'][0]))
        with self.assertRaises(GateError):self.build(data)

    def test_missing_index_is_not_created_by_search(self):
        with self.assertRaises(GateError):kb.search(self.index,'价格')
        self.assertFalse(self.index.exists())

    def test_native_template_layout_can_be_indexed_without_modifying_office(self):
        path=self.root/'template.potx'
        part='ppt/slideLayouts/slideLayout1.xml'
        with zipfile.ZipFile(path,'w') as z:
            z.writestr(part,'<p:sldLayout xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld name="Chart and commentary"><p:spTree><p:sp><p:nvSpPr><p:cNvPr id="2" name="Chart slot"/><p:nvPr><p:ph type="chart" idx="3"/></p:nvPr></p:nvSpPr></p:sp></p:spTree></p:cSld></p:sldLayout>')
        digest=hashlib.sha256(path.read_bytes()).hexdigest();data=self.catalog()
        data['sources']=[{'id':'source','path':path.name,'visibility':'local_only','sha256':digest}]
        card=data['cards'][0];card.update(kind='template',title='Chart layout',body='图表与分析区分栏。')
        card['sources']=[{'source_id':'source','part':part}]
        self.build(data);hit=kb.search(self.index,'图表',kind='template')['hits'][0]
        self.assertEqual(hit['sources'][0]['layout']['name'],'Chart and commentary')
        self.assertEqual(hit['sources'][0]['layout']['placeholders'][0]['type'],'chart')
        self.assertEqual(digest,hashlib.sha256(path.read_bytes()).hexdigest())
