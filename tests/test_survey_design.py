"""Behavior contracts for questionnaire and codebook handoffs."""
import copy
import unittest
from research_skills import survey_design as s
from research_skills.contracts import GateError, fingerprint


def fixture():
    return {
        "schema_version": 2, "meta": {"version": "1.0", "project": "Synthetic service study"},
        "populations": [{"key": "all", "name": "Eligible users"}],
        "objectives": [{"id": "O1", "decision": "Prioritize service improvements", "metric": "Reason distribution"}],
        "qc_plan": "Pilot and review contradictions; do not terminate by time alone.",
        "routing_cases": [
            {"id": "screenout", "population": "all", "answers": {"S1": 2}, "expected_visited": ["S1"]},
            {"id": "eligible", "population": "all", "answers": {"S1": 1, "Q1": [1], "Q2": "Slow"}, "expected_visited": ["S1", "Q1", "Q2"]}],
        "questions": [
            {"id": "S1", "population": "all", "module": "Screen", "type": "single",
             "text": "Have you used the service?", "objective_ids": ["O1"],
             "options": [{"code": 1, "label": "Yes"}, {"code": 2, "label": "No"}],
             "routes": [{"codes": [2], "target": "END"}]},
            {"id": "Q1", "population": "all", "module": "Experience", "type": "multi",
             "text": "Which aspects need improvement?", "objective_ids": ["O1"], "min_selections": 1,
             "max_selections": 2, "randomize": True,
             "options": [{"code": 1, "label": "Speed"},
                         {"code": 96, "label": "Other", "kind": "other", "specify": True, "fixed": True},
                         {"code": 99, "label": "None", "kind": "none", "exclusive": True, "fixed": True}]},
            {"id": "Q2", "population": "all", "module": "Experience", "type": "open",
             "text": "What happened?", "objective_ids": ["O1"]}],
    }


def approve(spec):
    spec["review"] = {"status": "approved", "content": True, "programming": True,
                      "analysis": True, "spec_sha256": s.spec_hash(spec)}
    return spec


class SurveyDesignTests(unittest.TestCase):
    def test_draft_checks_do_not_require_a_review(self):
        self.assertEqual(s.validate(fixture())["questions"], 3)

    def test_review_is_invalidated_by_an_option_edit(self):
        spec = approve(fixture())
        spec["questions"][1]["options"][0]["label"] = "Changed"
        with self.assertRaises(GateError): s.require_review(spec)

    def test_unknown_population_and_missing_objective_block(self):
        for field, value in [("population", "missing"), ("objective_ids", ["missing"])]:
            spec = fixture(); spec["questions"][0][field] = value
            with self.assertRaises(GateError): s.validate(spec)

    def test_other_can_coexist_but_none_must_be_exclusive(self):
        spec = fixture(); s.validate(spec)
        spec["questions"][1]["options"][-1]["exclusive"] = False
        with self.assertRaises(GateError): s.validate(spec)

    def test_backward_route_and_unknown_answer_code_block(self):
        for route in [{"codes": [1], "target": "S1"}, {"codes": [7], "target": "END"}]:
            spec = fixture(); spec["questions"][1]["routes"] = [route]
            with self.assertRaises(GateError): s.validate(spec)

    def test_dictionary_has_other_text_and_eligible_zero_semantics(self):
        rows = s.variables(fixture())
        by = {r["variable"]: r for r in rows}
        self.assertIn("all_Q1_other_96", by)
        self.assertIn("eligible", by["all_Q1_1"]["missing"])
        self.assertEqual(by["all_Q1_1"]["values"], {"0": "Not selected", "1": "Selected"})

    def test_route_simulation_distinguishes_screenout(self):
        self.assertEqual(s.simulate(fixture(), "all", {"S1": 2})["visited"], ["S1"])
        self.assertEqual(s.simulate(fixture(), "all", {"S1": 1, "Q1": [1], "Q2": "Slow"})["visited"], ["S1", "Q1", "Q2"])

    def test_route_simulation_rejects_exclusive_and_incomplete_answers(self):
        for answers in [{"S1": 1, "Q1": [1, 99]}, {"S1": 1}]:
            with self.assertRaises(GateError): s.simulate(fixture(), "all", answers)

    def test_codebook_binds_current_questionnaire(self):
        spec = fixture(); cb = s.draft_codebook(spec)
        spec["questions"][2]["text"] = "New wording"
        with self.assertRaises(GateError): s.validate_codebook(spec, cb)

    def test_codeframes_need_definitions_and_no_hierarchy_cycles(self):
        spec = fixture(); cb = s.draft_codebook(spec)
        cb["codeframes"] = [{"population": "all", "question_id": "Q2", "unit": "response",
            "mode": "multi", "codes": [{"code": "A", "label": "Delay", "definition": "", "include": "Wait", "exclude": "Price"}]}]
        with self.assertRaises(GateError): s.validate_codebook(spec, cb)
        cb["codeframes"][0]["codes"][0].update(definition="Delay", parent="A")
        with self.assertRaises(GateError): s.validate_codebook(spec, cb)

    def test_duplicate_variable_names_block(self):
        spec = fixture()
        q = copy.deepcopy(spec["questions"][2]); q["id"] = "Q1_1"
        spec["questions"].append(q)
        with self.assertRaises(GateError): s.variables(spec)

    def test_matrix_and_rank_storage_preserve_item_codes(self):
        spec = fixture(); q = spec["questions"][2]
        q.update(type="matrix", rows=[{"code": "speed", "label": "Speed"}],
                 options=[{"code": 1, "label": "Poor"}, {"code": 5, "label": "Good"}])
        self.assertIn("all_Q2_speed", [v["variable"] for v in s.variables(spec)])
        q.update(type="rank", rank_count=2)
        self.assertIn("all_Q2_5", [v["variable"] for v in s.variables(spec)])

    def test_export_checks_require_both_route_branches(self):
        spec = fixture(); s.check_paths(spec)
        spec["routing_cases"] = spec["routing_cases"][:1]
        with self.assertRaises(GateError): s.check_paths(spec)

    def test_overlapping_multi_answer_routes_are_ambiguous(self):
        spec = fixture(); spec["questions"][1]["routes"] = [
            {"codes": [1], "target": "Q2"}, {"codes": [96], "target": "END"}]
        with self.assertRaises(GateError): s.simulate(spec, "all", {"S1": 1, "Q1": [1, 96]})
