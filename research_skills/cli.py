"""File-based entrypoints for host agents and reproducible demos."""
import argparse
import json
from pathlib import Path
from . import workflows, demo
from .contracts import GateError
from . import survey_cli, study_cli, retrieval_cli


def main(argv=None):
    parser = argparse.ArgumentParser(prog="research-skills")
    commands = parser.add_subparsers(dest="command", required=True)
    survey_cli.register(commands)
    study_cli.register(commands)
    retrieval_cli.register(commands)
    for name,fields in {"demo":["output"], "qc":["input","plan","output"],
        "research":["plan","output"], "bind":["input","template","plan","output"],
        "questionnaire":["plan","output"], "translate":["input","plan","output"],
        "translation-units":["input","output"]}.items():
        command = commands.add_parser(name)
        for field in fields: command.add_argument("--"+field, required=True)
    args = parser.parse_args(argv)
    try:
        result = dispatch(args)
    except (GateError, ValueError, KeyError, OSError) as error:
        print(json.dumps({"status":"blocked", "reason":str(error) if isinstance(error, GateError) else type(error).__name__}))
        return 2
    print(json.dumps(result))
    return 0


def dispatch(args):
    if args.command in retrieval_cli.COMMANDS: return retrieval_cli.dispatch(args)
    if args.command in study_cli.COMMANDS: return study_cli.dispatch(args)
    if args.command in survey_cli.COMMANDS: return survey_cli.dispatch(args)
    if args.command == "demo": return demo.run(args.output)
    if args.command == "translation-units":
        output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x") as stream:
            json.dump(workflows.translation_units(args.input), stream, indent=2)
        return {"units_file":str(output)}
    plan = json.loads(Path(args.plan).read_text())
    if args.command == "qc": return workflows.qc(args.input, plan, args.output)
    if args.command == "research": return workflows.research(plan, args.output)
    if args.command == "bind": return workflows.bind(args.input, args.template, plan, args.output)
    if args.command == "questionnaire": return workflows.questionnaire(plan, args.output)
    if args.command == "translate": return workflows.translate(args.input, plan, args.output)
    raise GateError("Unknown workflow")
