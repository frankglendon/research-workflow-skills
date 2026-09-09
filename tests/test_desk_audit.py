import copy
import unittest
from research_skills.desk_audit import audit


class DeskAuditTests(unittest.TestCase):
    def setUp(self):
        self.study = {"questions": [{"id": "Q1"}], "claim_ids": ["F1"],
            "pages": [{"id": "P1", "role": "competitor", "question_ids": ["Q1"],
                       "claim_ids": ["F1"], "finding": "Observed assortment", "implication": "Comparison by shopping task"}],
            "answers": [{"id": "A1", "question_id": "Q1", "status": "partial", "answer": "Supported mechanism, unmeasured performance", "page_ids": ["P1"]}]}

    def codes(self, study=None):
        return {x["code"] for x in audit(study or self.study)["findings"]}

    def test_structure_is_not_semantic_certification(self):
        result = audit(self.study)
        self.assertEqual(result["status"], "structure_checked")
        self.assertEqual(result["semantic_quality"], "not_assessed_by_code")

    def test_plan_cannot_answer_business_question(self):
        self.study["pages"][0]["role"] = "future_research"
        self.assertTrue({"unanswered_question", "plan_dominates", "invalid_answer_support"} <= self.codes())

    def test_cross_question_support_is_rejected(self):
        self.study["questions"].append({"id": "Q2"})
        self.study["pages"][0]["question_ids"] = ["Q2"]
        self.assertIn("invalid_answer_support", self.codes())

    def test_unknown_claim_is_reported(self):
        self.study["pages"][0]["claim_ids"] = ["invented"]
        self.assertIn("unknown_claim", self.codes())

    def test_duplicate_id_is_reported(self):
        self.study["pages"].append(copy.deepcopy(self.study["pages"][0]))
        self.assertIn("invalid_id", self.codes())

    def test_unresolved_is_explicit_not_silently_passed(self):
        self.study["pages"] = []
        self.study["answers"][0].update(status="unresolved", page_ids=[])
        self.assertIn("unanswered_question", self.codes())
        self.assertNotIn("unsupported_answer", self.codes())

    def test_absent_business_questions_is_not_valid_report(self):
        self.assertIn("no_questions", self.codes({"pages": [], "questions": [], "answers": []}))
