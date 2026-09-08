"""Project-scoped SkillOpt adapter; only reviewed curated tasks enter replay."""
import argparse
import json
from pathlib import Path
import sys
from .contracts import GateError, fingerprint


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, help="Local SkillOpt source checkout")
    parser.add_argument("--skill", required=True)
    parser.add_argument("--backend", choices=["mock", "codex"], default="mock")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    target = (root / "skills" / args.skill / "SKILL.md").resolve()
    if target.parent.parent != root / "skills" or not target.is_file():
        raise GateError("Unknown skill target")
    sys.path.insert(0, str(Path(args.engine).resolve()))
    from skillopt_sleep.config import DEFAULTS, SleepConfig
    from skillopt_sleep.tasks_file import load_tasks_file
    from skillopt_sleep.cycle import run_sleep_cycle
    task_file = root / "evals" / (args.skill + ".json")
    tasks, metadata = load_tasks_file(str(task_file))
    if metadata.get("reviewed") is not True or metadata.get("dataset_kind") != "curated_synthetic":
        raise GateError("Only reviewed curated synthetic tasks are accepted")
    for task in tasks:
        task.project = str(root)
        task.skill_hint = args.skill
    config = dict(DEFAULTS)
    config.update(invoked_project=str(root), projects="invoked", backend=args.backend,
        target_skill_path=str(target), state_dir=str(root / ".skillopt-sleep/state" / args.skill),
        evolve_memory=False, evolve_skill=True, gate_mode="on", gate_metric="hard",
        gate_no_regression=True, edit_budget=2, max_tasks_per_night=8,
        max_tokens_per_night=24000, auto_adopt=False, llm_mine=False, recall_k=0,
        dream_factor=0, progress=True, evidence_log=True, evidence_max_chars=1000,
        replay_mode="mock" if args.backend == "mock" else "codex-text",
        preferences="Keep concise English workflow instructions, CLI commands and hard gates. No emoji. Do not weaken evidence, coverage, immutability or Office validation. Optimize transferable decisions, never embed evaluation answers.")
    before = fingerprint(target.read_bytes())
    outcome = run_sleep_cycle(SleepConfig(config), seed_tasks=tasks, dry_run=args.dry_run)
    if fingerprint(target.read_bytes()) != before:
        raise GateError("Optimization unexpectedly modified a live skill")
    report = outcome.report
    result = {"skill": args.skill, "backend": args.backend, "dataset_kind": "curated_synthetic",
        "sessions": 0, "tasks": len(tasks), "baseline": report.baseline_score,
        "candidate": report.candidate_score, "accepted": report.accepted,
        "gate_action": report.gate_action, "adopted": outcome.adopted,
        "holdout_leaked": report.holdout_leaked,
        "replay_mode": config["replay_mode"],
        "staging": outcome.staging_dir, "skill_sha256": before,
        "dataset_sha256": fingerprint(task_file.read_bytes())}
    if outcome.staging_dir:
        evidence_path = Path(outcome.staging_dir) / "evidence.jsonl"
        if evidence_path.is_file():
            events = [json.loads(line) for line in evidence_path.read_text().splitlines()]
            tests = [event for event in events if event.get("stage") == "test"
                     and event.get("event") == "held_out_score"]
            if tests:
                result["final_test"] = {key: tests[-1][key] for key in ("n_test", "hard", "soft")}
    folder = root / ".skillopt-sleep/results"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{args.skill}-{args.backend}.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
