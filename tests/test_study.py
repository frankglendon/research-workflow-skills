import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research_skills import study
from research_skills.contracts import GateError


def plan():
    return {"schema_version": 1, "study_id": "study-001", "stages": [
        {"id": "design", "depends_on": [], "inputs": ["brief.md"],
         "required_artifacts": ["outline"], "review_mode": "separate_execution",
         "acceptance": [{"id": "coverage", "description": "Every decision has a measurement"}]},
        {"id": "codebook", "depends_on": ["design"], "inputs": [],
         "required_artifacts": ["datamap"], "review_mode": "host",
         "acceptance": [{"id": "variables", "description": "Variables match the design"}]}]}


class StudyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "brief.md").write_text("synthetic brief")
        (self.root / "outline.md").write_text("synthetic outline")
        (self.root / "datamap.json").write_text('{"synthetic":true}')
        study.initialize(self.root, plan())

    def rev(self):
        return study.status(self.root)["revision"]

    def candidate(self, stage="design"):
        return next(s for s in study.status(self.root)["stages"] if s["id"] == stage)["candidate_sha256"]

    def submit(self, stage="design"):
        study.start(self.root, stage, "build-001", self.rev())
        item = {"id": "outline", "path": "outline.md"} if stage == "design" else {"id": "datamap", "path": "datamap.json"}
        study.submit(self.root, stage, [item], self.rev())

    def review(self, stage="design", verdict="passed", execution="review-001"):
        return study.review(self.root, stage, {"candidate_sha256": self.candidate(stage),
            "execution_id": execution, "criteria": [{"id": "coverage" if stage == "design" else "variables",
                "verdict": verdict, "reason": "Synthetic fixture review"}]}, self.rev())

    def finish(self, stage="design"):
        self.submit(stage); self.review(stage)
        study.complete(self.root, stage, self.rev())

    def test_resume_reads_persisted_phase_without_advancing(self):
        self.submit()
        before = (self.root / ".research-workflow/state.sqlite3").read_bytes()
        result = study.status(self.root)
        self.assertEqual(result["stages"][0]["status"], "review")
        self.assertEqual(result["stages"][0]["action"], "review")
        self.assertEqual(before, (self.root / ".research-workflow/state.sqlite3").read_bytes())

    def test_missing_dependency_blocks_start_without_state_change(self):
        with self.assertRaises(GateError): study.start(self.root, "codebook", "build-001", 0)
        self.assertEqual(self.rev(), 0)

    def test_review_coverage_and_failed_verdict_cannot_complete(self):
        self.submit(); revision = self.rev()
        for criteria in [[], [{"id": "wrong", "verdict": "passed", "reason": "x"}],
                [{"id": "coverage", "verdict": "passed", "reason": "x"}] * 2]:
            with self.assertRaises(GateError):
                study.review(self.root, "design", {"candidate_sha256": self.candidate(),
                    "execution_id": "review-001", "criteria": criteria}, revision)
        self.assertEqual(self.rev(), revision)
        self.review(verdict="failed")
        with self.assertRaises(GateError): study.complete(self.root, "design", self.rev())
        self.assertEqual(study.status(self.root)["stages"][0]["action"], "revise")

    def test_distinct_execution_is_required_but_only_declared(self):
        self.submit()
        with self.assertRaises(GateError): self.review(execution="build-001")
        self.review()
        study.complete(self.root, "design", self.rev())
        self.assertEqual(study.manifest(self.root)["review_identity"], "host_declared_not_authenticated")

    def test_artifact_edit_after_review_invalidates_completion(self):
        self.submit(); self.review()
        (self.root / "outline.md").write_text("changed after review")
        with self.assertRaises(GateError): study.complete(self.root, "design", self.rev())
        self.assertEqual(study.status(self.root)["stages"][0]["status"], "stale")

    def test_input_edit_during_build_requires_new_start(self):
        study.start(self.root, "design", "build-001", self.rev())
        (self.root / "brief.md").write_text("changed brief")
        with self.assertRaises(GateError):
            study.submit(self.root, "design", [{"id": "outline", "path": "outline.md"}], self.rev())

    def test_upstream_revision_invalidates_descendants_only(self):
        self.finish(); self.finish("codebook")
        self.assertTrue(study.status(self.root)["complete"])
        study.start(self.root, "design", "build-002", self.rev())
        self.assertEqual(study.status(self.root)["stages"][1]["status"], "stale")
        self.finish()
        self.assertEqual(study.status(self.root)["stages"][1]["status"], "stale")

    def test_stale_review_candidate_and_revision_are_rejected(self):
        self.submit(); old = self.candidate(); revision = self.rev()
        self.review()
        with self.assertRaises(GateError): study.complete(self.root, "design", revision)
        self.submit()
        with self.assertRaises(GateError):
            study.review(self.root, "design", {"candidate_sha256": old, "execution_id": "review-002",
                "criteria": [{"id": "coverage", "verdict": "passed", "reason": "old"}]}, self.rev())

    def test_review_is_bound_to_one_study_even_with_identical_files(self):
        self.submit(); previous = self.candidate()
        other = self.root / "other"; other.mkdir()
        for name in ["brief.md", "outline.md"]:
            (other / name).write_bytes((self.root / name).read_bytes())
        study.initialize(other, plan())
        study.start(other, "design", "build-001", 0)
        study.submit(other, "design", [{"id": "outline", "path": "outline.md"}], 1)
        self.assertNotEqual(previous, study.status(other)["stages"][0]["candidate_sha256"])

    def test_amend_requirements_keeps_unaffected_completion(self):
        self.finish(); self.finish("codebook")
        changed = plan(); changed["stages"][1]["acceptance"][0]["description"] = "New requirement"
        study.amend(self.root, changed, self.rev())
        phases = {s["id"]: s["status"] for s in study.status(self.root)["stages"]}
        self.assertEqual(phases, {"design": "complete", "codebook": "pending"})

    def test_cycles_and_unknown_fields_are_rejected(self):
        for dependency in ["codebook", "unknown"]:
            changed = plan(); changed["stages"][0]["depends_on"] = [dependency]
            with self.assertRaises(GateError): study.amend(self.root, changed, 0)
        changed = plan(); changed["stages"][0]["review_mod"] = "host"
        with self.assertRaises(GateError): study.amend(self.root, changed, 0)

    def test_unsafe_paths_and_missing_artifacts_are_rejected(self):
        study.start(self.root, "design", "build-001", self.rev())
        for path in ["../outside.md", "/tmp/elsewhere.md", "missing.md", ".research-workflow/state.sqlite3"]:
            with self.assertRaises(GateError):
                study.submit(self.root, "design", [{"id": "outline", "path": path}], self.rev())
        with self.assertRaises(GateError): study.submit(self.root, "design", [], self.rev())

    def test_invalid_office_file_cannot_be_submitted(self):
        (self.root / "bad.docx").write_bytes(b"not office")
        study.start(self.root, "design", "build-001", self.rev())
        with self.assertRaises(GateError):
            study.submit(self.root, "design", [{"id": "outline", "path": "bad.docx"}], self.rev())
        self.assertEqual(study.status(self.root)["stages"][0]["status"], "active")

    def test_transaction_failure_preserves_last_checkpoint(self):
        persist = study._persist
        def fail_after_writing(*args):
            persist(*args)
            raise RuntimeError("simulated interruption")
        before = study.manifest(self.root)
        with patch.object(study, "_persist", side_effect=fail_after_writing):
            with self.assertRaises(RuntimeError): study.start(self.root, "design", "build-001", 0)
        self.assertEqual(study.manifest(self.root), before)

    def test_symlink_artifact_cannot_replace_a_source(self):
        (self.root / "link.md").symlink_to(self.root / "outline.md")
        study.start(self.root, "design", "build-001", self.rev())
        with self.assertRaises(GateError):
            study.submit(self.root, "design", [{"id": "outline", "path": "link.md"}], self.rev())

    def test_nested_submission_state_is_informative_not_authenticated(self):
        self.submit()
        bad = {"candidate_sha256": self.candidate(), "execution_id": "review-002",
            "criteria": [{"id": "coverage", "verdict": True, "reason": "not a valid enum"}]}
        with self.assertRaises(GateError): study.review(self.root, "design", bad, self.rev())

    def test_manifest_and_events_exclude_raw_review_and_paths(self):
        self.finish()
        report = study.manifest(self.root)
        text = json.dumps(report)
        for private in ["Synthetic fixture review", "synthetic brief", "outline.md", "build-001", str(self.root)]:
            self.assertNotIn(private, text)
        self.assertGreater(len(report["events"]), 0)
        self.assertFalse(report["complete"])

    def test_initialization_never_overwrites_an_existing_study(self):
        with self.assertRaises(GateError): study.initialize(self.root, plan())
        self.assertEqual(self.rev(), 0)
