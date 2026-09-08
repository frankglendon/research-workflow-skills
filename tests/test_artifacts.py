from pathlib import Path
import tempfile
import unittest
import openpyxl
from research_skills.artifacts import export_artifact
from research_skills.contracts import GateError


class ArtifactTests(unittest.TestCase):
    def test_source_change_during_export_blocks_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "source.txt", root / "output.xlsx"
            source.write_text("original")
            def build(path, run_id):
                openpyxl.Workbook().save(path)
                source.write_text("concurrent change")
            with self.assertRaises(GateError):
                export_artifact(output, build, tool="test", inputs=[source], config={})
            self.assertFalse(output.exists())
            self.assertFalse(output.with_suffix(".xlsx.manifest.json").exists())
