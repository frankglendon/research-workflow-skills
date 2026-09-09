from pathlib import Path
import tempfile
import unittest

from research_skills import study_eval
from research_skills.contracts import GateError


class StudyEvalTests(unittest.TestCase):
    def test_reliability_is_not_any_attempt_success(self):
        result = study_eval.metrics([True, False, True], 2)
        self.assertEqual(result["pass_at_k"], 1)
        self.assertAlmostEqual(result["all_k_pass_estimate"], 1 / 3)
        self.assertAlmostEqual(result["single_run_pass_rate"], 2 / 3)
        self.assertFalse(result["all_runs_passed"])

    def test_metrics_require_complete_boolean_runs_and_valid_k(self):
        for values, k in [([], 1), (["true"], 1), ([True], 0), ([True], 2), ([True], True)]:
            with self.assertRaises(GateError): study_eval.metrics(values, k)

    def test_summary_requires_unique_complete_runs_with_one_version(self):
        rows = [{"run_id": f"run-{n}", "task_id": "task-01", "skill_sha256": "a" * 64,
                 "dataset_sha256": "b" * 64, "passed": n == 1} for n in [1, 2]]
        payload = {"schema_version": 1, "run_kind": "model_replay", "runs": rows}
        result = study_eval.summarize(payload, 2)
        self.assertEqual(result["tasks"][0]["metrics"]["pass_at_k"], 1)
        self.assertEqual(result["tasks"][0]["metrics"]["all_k_pass_estimate"], 0)
        for key, value in [("skill_sha256", "c" * 64), ("dataset_sha256", "d" * 64), ("run_id", "run-1")]:
            old = rows[1][key]; rows[1][key] = value
            with self.assertRaises(GateError): study_eval.summarize(payload, 2)
            rows[1][key] = old
        rows[1]["task_id"] = "task-02"
        with self.assertRaises(GateError): study_eval.summarize(payload, 2)

    def test_repeated_scenarios_use_distinct_workspaces(self):
        with tempfile.TemporaryDirectory() as directory:
            result = study_eval.run(Path(directory) / "eval", repeats=2)
            self.assertEqual(result["model_calls"], 0)
            self.assertEqual(result["scenarios"], 6)
            self.assertEqual(result["runs"], 12)
            self.assertEqual(result["passed_runs"], 12)
            self.assertTrue(result["all_runs_passed"])
            self.assertFalse(result["semantic_quality_measured"])
            self.assertEqual(len(list((Path(directory) / "eval").glob("*/.research-workflow/state.sqlite3"))), 12)
            with self.assertRaises(GateError): study_eval.run(Path(directory) / "eval", repeats=2)
