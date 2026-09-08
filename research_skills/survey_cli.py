"""Shared survey/codebook CLI, also embedded in the private host package."""
import json
from pathlib import Path
from . import survey_design as design, survey_export as export

COMMANDS = {"survey-demo": ["output"], "survey-check": ["spec"], "survey-run": ["spec", "output"],
            "survey-simulate": ["spec", "cases"], "codebook-draft": ["spec", "output"],
            "codebook-check": ["spec", "codebook"], "codebook-run": ["spec", "codebook", "output"],
            "datamap-inspect": ["input", "output"]}


def register(commands):
    for name, fields in COMMANDS.items():
        parser = commands.add_parser(name)
        for field in fields:
            parser.add_argument("--" + field, required=True)


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _save(path, data):
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
    return {"artifact": str(target.resolve())}


def dispatch(args):
    if args.command == "survey-demo":
        root = Path(__file__).resolve().parents[1]
        examples = root / "examples"
        if not examples.exists(): examples = root / "evals/examples"
        spec, plan = _read(examples / "survey-v2.json"), _read(examples / "codebook-v1.json")
        folder = Path(args.output)
        design.need(not folder.exists(), "Demo output directory already exists")
        q = export.questionnaire(spec, folder / "questionnaire.xlsx")
        c = export.codebook(spec, plan, folder / "codebook.xlsx")
        result = {"synthetic": True, "model_calls": 0, "exports": 2, "openxml_errors": q["openxml_errors"] + c["openxml_errors"],
                  "questions": len(spec["questions"]), "variables": len(plan["variables"]), **design.check_paths(spec)}
        _save(folder / "summary.json", result)
        return result
    if args.command == "datamap-inspect": return _save(args.output, export.inspect_datamap(args.input))
    spec = _read(args.spec)
    if args.command == "survey-check": return {"passed": True, **design.validate(spec), "variables": len(design.variables(spec))}
    if args.command == "survey-run": return export.questionnaire(spec, args.output)
    if args.command == "codebook-draft": return _save(args.output, design.draft_codebook(spec))
    if args.command == "codebook-check": return {"passed": True, **design.validate_codebook(spec, _read(args.codebook))}
    if args.command == "codebook-run": return export.codebook(spec, _read(args.codebook), args.output)
    if args.command == "survey-simulate":
        cases = _read(args.cases)
        design.need(cases, "Provide at least one reviewed routing test case")
        results = []
        for case in cases:
            actual = design.simulate(spec, case["population"], case["answers"])
            design.need(actual["visited"] == case["expected_visited"], "Routing case differs from expected path")
            results.append({"id": case["id"], "passed": True, "visited": actual["visited"], "skipped": actual["skipped"]})
        return {"passed": True, "cases": results}
    raise ValueError("Unknown survey command")
