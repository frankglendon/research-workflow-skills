import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research_skills.study_eval import example_plan


class StudyCliTests(unittest.TestCase):
    def test_separate_process_resume_then_refusal_has_structured_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plan.json").write_text(json.dumps(example_plan()))
            (root / "brief.md").write_text("synthetic brief")
            def run(*args):
                result = subprocess.run([sys.executable, "-m", "research_skills", *args],
                    capture_output=True, text=True, check=False)
                return result.returncode, json.loads(result.stdout)
            code, result = run("study-init", "--workspace", str(root), "--plan", str(root / "plan.json"))
            self.assertEqual(code, 0)
            code, _ = run("study-start", "--workspace", str(root), "--stage", "design", "--execution", "run-01", "--revision", "0")
            self.assertEqual(code, 0)
            code, result = run("study-inspect", "--workspace", str(root), "--stage", "design")
            self.assertEqual(result["current"]["status"], "active")
            self.assertEqual(result["spec"]["acceptance"][0]["id"], "coverage")
            code, result = run("study-complete", "--workspace", str(root), "--stage", "design", "--revision", "1")
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "blocked")
            self.assertNotIn(str(root), json.dumps(result))
            code, result = run("study-status", "--workspace", str(root))
            self.assertEqual(result["revision"], 1)
