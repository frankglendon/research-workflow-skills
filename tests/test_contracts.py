import unittest
from research_skills.contracts import GateError, review_rows, validate_evidence


class ReviewTests(unittest.TestCase):
    def test_missing_review_blocks(self):
        with self.assertRaises(GateError):
            review_rows([2, 3], [{"row": 2, "verdict": "clean"}])

    def test_duplicate_review_blocks(self):
        with self.assertRaises(GateError):
            review_rows([2], [{"row": 2, "verdict": "clean"}] * 2)

    def test_uncertain_is_distinct_from_clean(self):
        rows = [{"row": 2, "verdict": "uncertain", "findings": []}]
        self.assertEqual(review_rows([2], rows)[0]["verdict"], "uncertain")

    def test_fabricated_quote_blocks(self):
        ledger = {"documents": [{"id": "d1", "url": "https://example.org/data",
                  "text": "Revenue is 100 USD."}], "claims": [{"id": "c1",
                  "statement": "Revenue is 900 USD.", "status": "supported",
                  "evidence": [{"document_id": "d1", "quote": "Revenue is 900 USD."}]}]}
        with self.assertRaises(GateError):
            validate_evidence(ledger)
