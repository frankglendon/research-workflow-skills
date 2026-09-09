import json
from pathlib import Path
import tempfile
import unittest

from research_skills.optimize import select_dataset, replay_health
from research_skills.contracts import GateError


class OptimizationDatasetTests(unittest.TestCase):
    def test_only_explicit_reviewed_synthetic_repo_datasets_are_selected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "evals").mkdir()
            chosen = root / "evals/runtime-v1.json"
            chosen.write_text(json.dumps({"reviewed": True, "dataset_kind": "curated_synthetic"}))
            self.assertEqual(select_dataset(root, "workflow", "evals/runtime-v1.json"), chosen.resolve())
            for value in ["../outside.json", "missing.json"]:
                with self.assertRaises(GateError): select_dataset(root, "workflow", value)
            chosen.write_text(json.dumps({"reviewed": False, "dataset_kind": "curated_synthetic"}))
            with self.assertRaises(GateError): select_dataset(root, "workflow", "evals/runtime-v1.json")

    def test_default_dataset_cannot_follow_a_symlink_outside_evals(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / "evals").mkdir()
            outside = root / "outside.json"
            outside.write_text(json.dumps({"reviewed": True, "dataset_kind": "curated_synthetic"}))
            (root / "evals/workflow.json").symlink_to(outside)
            with self.assertRaises(GateError): select_dataset(root, "workflow")

    def test_failed_model_calls_invalidate_evaluation(self):
        events = [{"event": "model_call", "cache_hit": False, "response": "", "error": "CLI unavailable"}]
        self.assertEqual(replay_health(events), {"valid": False, "failed_calls": 1, "observed_calls": 1})
        self.assertFalse(replay_health([])["valid"])

    def test_real_response_without_call_errors_is_valid(self):
        events = [{"event": "model_call", "response": "{}", "error": ""},
                  {"event": "model_call", "cache_hit": True}]
        self.assertEqual(replay_health(events), {"valid": True, "failed_calls": 0, "observed_calls": 1})
