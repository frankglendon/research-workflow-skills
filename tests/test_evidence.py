import unittest
from research_skills.contracts import GateError, fingerprint, validate_evidence


def ledger():
    text = "Acme revenue was 100 USD in 2025."
    evidence = [{"document_id": "d1", "quote": text}]
    return {"documents": [{"id": "d1", "url": "https://example.org/report", "text": text,
            "sha256": fingerprint(text.encode())}], "claims": [{"id": "c1", "statement": text,
            "status": "supported", "scope": {"year": 2025, "unit": "USD", "entity": "Acme"},
            "evidence": evidence, "evidence_sha256": fingerprint(evidence),
            "reviewed_statement_sha256": fingerprint(text.encode()), "semantic_reviewed": True}]}


class EvidenceTests(unittest.TestCase):
    def test_valid_bound_evidence_passes(self):
        self.assertEqual(validate_evidence(ledger())["claims"], 1)

    def test_text_false_is_not_a_completed_review(self):
        data = ledger()
        data["claims"][0]["semantic_reviewed"] = "false"
        with self.assertRaises(GateError):
            validate_evidence(data)

    def test_forged_quote_on_existing_url_blocks(self):
        data = ledger()
        data["claims"][0]["evidence"][0]["quote"] = "Acme revenue was 900 USD in 2025."
        with self.assertRaisesRegex(GateError, "does not occur"):
            validate_evidence(data)

    def test_review_cannot_be_reused_after_statement_changes(self):
        data = ledger()
        data["claims"][0]["statement"] = "Acme revenue was 100 EUR in 2025."
        with self.assertRaises(GateError):
            validate_evidence(data)
