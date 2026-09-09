"""Optional study lifecycle commands; legacy file exports remain independently usable."""
import json
from pathlib import Path

from . import study, study_eval
from .contracts import GateError

COMMANDS = {
    "study-init": ["workspace", "plan"], "study-status": ["workspace"],
    "study-inspect": ["workspace", "stage"],
    "study-start": ["workspace", "stage", "execution", "revision"],
    "study-submit": ["workspace", "stage", "artifacts", "revision"],
    "study-review": ["workspace", "stage", "review", "revision"],
    "study-complete": ["workspace", "stage", "revision"],
    "study-amend": ["workspace", "plan", "revision"],
    "study-export": ["workspace", "output"], "study-demo": ["output"],
    "study-eval-summary": ["results", "k", "output"],
}


def register(commands):
    for name, fields in COMMANDS.items():
        parser = commands.add_parser(name)
        for field in fields:
            parser.add_argument("--" + field, required=True, type=int if field in {"revision", "k"} else str)
        if name == "study-demo":
            parser.add_argument("--repeats", type=int, default=3)


def _read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _save(path, payload):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
    return payload


def dispatch(args):
    name = args.command
    if name == "study-demo":
        result = study_eval.run(args.output, args.repeats)
        if not result["all_runs_passed"]:
            raise GateError("Repeated lifecycle checks failed; inspect the saved summary")
        return {key: value for key, value in result.items() if key != "cases"}
    if name == "study-eval-summary":
        result = study_eval.summarize(_read(args.results), args.k)
        return _save(args.output, result)
    if name == "study-init": return study.initialize(args.workspace, _read(args.plan))
    if name == "study-status": return study.status(args.workspace)
    if name == "study-inspect": return study.inspect_stage(args.workspace, args.stage)
    if name == "study-start": return study.start(args.workspace, args.stage, args.execution, args.revision)
    if name == "study-submit": return study.submit(args.workspace, args.stage, _read(args.artifacts), args.revision)
    if name == "study-review": return study.review(args.workspace, args.stage, _read(args.review), args.revision)
    if name == "study-complete": return study.complete(args.workspace, args.stage, args.revision)
    if name == "study-amend": return study.amend(args.workspace, _read(args.plan), args.revision)
    if name == "study-export": return _save(args.output, study.manifest(args.workspace))
    raise GateError("Unknown study command")
