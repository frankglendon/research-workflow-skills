"""Behavior checks for country lists and nested brand funnels."""
import copy
import unittest
from research_skills import survey_design as s
from research_skills.contracts import GateError
from tests.test_survey_design import fixture


def instrument():
    spec = fixture()
    spec['questions'] = spec['questions'][:2]
    q = spec['questions'][1]
    q['routes'] = []
    q['options'] = [{'code': 1, 'label': 'Brand A'},
                    {'code': 2, 'label': 'Country-specific brand',
                     'show_if': [{'question_id': 'S1', 'codes': [1]}]},
                    {'code': 99, 'label': 'None', 'kind': 'none', 'exclusive': True, 'fixed': True}]
    q['text'] = 'Which brands do you know?'
    later = copy.deepcopy(q)
    later.update(id='Q2', text='Which have you bought?',
                 options_from={'question_id': 'Q1', 'always_codes': [99]})
    spec['questions'].append(later)
    return spec


class CarryForwardTests(unittest.TestCase):
    def test_negative_condition_requires_an_actual_prior_answer(self):
        spec = instrument()
        spec['questions'][2]['show_if'] = [{'question_id': 'Q1', 'codes': [2], 'operator': 'not_any'}]
        self.assertIn('Q2', s.simulate(spec, 'all', {'S1': 1, 'Q1': [1], 'Q2': [99]})['visited'])
        self.assertNotIn('Q2', s.simulate(spec, 'all', {'S1': 1, 'Q1': [2]})['visited'])
        spec['questions'][1]['show_if'] = [{'question_id': 'S1', 'codes': [2]}]
        self.assertEqual(s.simulate(spec, 'all', {'S1': 1})['visited'], ['S1'])

    def test_unaware_brand_cannot_enter_purchase_funnel(self):
        with self.assertRaises(GateError):
            s.simulate(instrument(), 'all', {'S1': 1, 'Q1': [1], 'Q2': [2]})

    def test_selected_and_fixed_none_remain_available(self):
        spec = instrument()
        for selected in [[1], [99]]:
            self.assertEqual(s.simulate(spec, 'all', {'S1': 1, 'Q1': [1], 'Q2': selected})['visited'], ['S1', 'Q1', 'Q2'])

    def test_country_filter_rejects_hidden_option(self):
        spec = instrument()
        spec['questions'][0]['routes'] = []
        with self.assertRaises(GateError):
            s.simulate(spec, 'all', {'S1': 2, 'Q1': [2], 'Q2': [99]})

    def test_bad_carry_forward_reference_fails_before_execution(self):
        for source in ['Q2', 'absent', 'S1']:
            spec = instrument()
            spec['questions'][2]['options_from']['question_id'] = source
            with self.assertRaises(GateError): s.validate(spec)

    def test_unknown_country_filter_code_fails_validation(self):
        spec = instrument()
        spec['questions'][1]['options'][1]['show_if'][0]['codes'] = [88]
        with self.assertRaises(GateError): s.validate(spec)

    def test_matrix_asks_only_selected_rows(self):
        spec = instrument()
        spec['questions'][2] = dict(id='Q2', population='all', module='Experience',
            text='Rate the brands you know', type='matrix', objective_ids=['O1'],
            rows=[{'code': 1, 'label': 'Brand A'}, {'code': 2, 'label': 'Brand B'}],
            options=[{'code': 1, 'label': 'Good'}, {'code': 2, 'label': 'Poor'}],
            rows_from={'question_id': 'Q1', 'always_codes': []})
        self.assertTrue(s.simulate(spec, 'all', {'S1': 1, 'Q1': [1], 'Q2': {'1': 1}})['complete'])
        with self.assertRaises(GateError):
            s.simulate(spec, 'all', {'S1': 1, 'Q1': [1], 'Q2': {'1': 1, '2': 2}})

    def test_dictionary_carries_eligibility_and_does_not_imply_zero(self):
        rows = {r['variable']: r for r in s.variables(instrument())}
        self.assertEqual(rows['all_Q2_2']['options_from']['question_id'], 'Q1')
        self.assertEqual(rows['all_Q2_2']['option_show_if'][0]['question_id'], 'S1')
        self.assertIn('not displayed', rows['all_Q2_2']['missing'])

    def test_empty_filtered_matrix_is_not_a_completed_answer(self):
        spec = instrument()
        spec['questions'][2] = dict(id='Q2', population='all', module='Experience',
            text='Rate experienced touchpoints', type='matrix', objective_ids=['O1'],
            rows=[{'code': 1, 'label': 'Touchpoint'}],
            options=[{'code': 1, 'label': 'Good'}, {'code': 2, 'label': 'Poor'}],
            rows_from={'question_id': 'Q1', 'always_codes': []})
        with self.assertRaises(GateError):
            s.simulate(spec, 'all', {'S1': 1, 'Q1': [99], 'Q2': {}})
