import tempfile
from pathlib import Path
import unittest
import openpyxl
from research_skills import survey_design as s, survey_export as out
from research_skills.contracts import GateError
from test_survey_design import fixture, approve


class SurveyExportTests(unittest.TestCase):
    def test_questionnaire_codebook_are_office_valid_and_long_datamap(self):
        spec = approve(fixture())
        plan = approve(s.draft_codebook(spec))
        with tempfile.TemporaryDirectory() as folder:
            qpath, cpath = Path(folder) / "questionnaire.xlsx", Path(folder) / "codebook.xlsx"
            self.assertEqual(out.questionnaire(spec, qpath)["openxml_errors"], 0)
            self.assertEqual(out.codebook(spec, plan, cpath)["openxml_errors"], 0)
            book = openpyxl.load_workbook(cpath)
            self.assertEqual(book["Datamap"]["D1"].value, "Answer Code")
            self.assertEqual(out.inspect_datamap(cpath)["layouts"][0]["layout"], "long_datamap")
            book.close()

    def test_unreviewed_codebook_cannot_export(self):
        spec = approve(fixture())
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(GateError): out.codebook(spec, s.draft_codebook(spec), Path(folder) / "blocked.xlsx")
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_question_text_cannot_become_a_formula(self):
        spec = fixture(); spec["questions"][0]["text"] = '=HYPERLINK("https://example.com", "text")'; approve(spec)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "safe.xlsx"
            out.questionnaire(spec, path)
            book = openpyxl.load_workbook(path)
            self.assertEqual(book["Questionnaire"]["E2"].data_type, "s")
            book.close()

    def test_preserve_existing_program_variable_names(self):
        spec = fixture(); spec["variable_names"] = {"all_S1": "Screen.Consent"}
        self.assertEqual(s.variables(spec)[0]["variable"], "Screen.Consent")
        spec["variable_names"]["missing"] = "X"
        with self.assertRaises(GateError): s.variables(spec)
