"""Repeat synthetic study-lifecycle scenarios; this is not model-quality evaluation."""
import json
import re
from math import comb
from pathlib import Path

from . import study
from .contracts import GateError


def metrics(results, k):
    study.need(isinstance(results, list) and results and all(type(r) is bool for r in results),
               "Metrics require non-empty boolean run outcomes")
    n, c = len(results), sum(results)
    study.need(type(k) is int and 1 <= k <= n, "k must be between 1 and the observed run count")
    return {"n": n, "c": c, "k": k, "single_run_pass_rate": c / n,
        "pass_at_k": 1 - (comb(n - c, k) if n - c >= k else 0) / comb(n, k),
        "all_k_pass_estimate": (comb(c, k) if c >= k else 0) / comb(n, k),
        "all_runs_passed": c == n}


def summarize(payload, k):
    """Aggregate declared run outcomes; do not manufacture missing runs or grade artifacts."""
    study.exact(payload, {"schema_version", "run_kind", "runs"}, "Evaluation results")
    study.need(type(payload["schema_version"]) is int and payload["schema_version"] == 1, "Unknown evaluation schema")
    study.need(payload["run_kind"] in ("deterministic_fixture", "model_replay", "human_reviewed_artifact"), "Declare the evaluation kind")
    study.need(isinstance(payload["runs"], list) and payload["runs"], "Provide observed runs")
    groups, versions, seen = {}, set(), set()
    for row in payload["runs"]:
        study.exact(row, {"task_id", "run_id", "skill_sha256", "dataset_sha256", "passed"}, "Observed run")
        study.identifier(row["task_id"]); study.identifier(row["run_id"])
        for field in ("skill_sha256", "dataset_sha256"):
            study.need(isinstance(row[field], str) and re.fullmatch(r"[0-9a-f]{64}", row[field]), "Bind results to skill and dataset hashes")
        study.need(type(row["passed"]) is bool, "Observed outcomes must be boolean")
        key = (row["task_id"], row["run_id"])
        study.need(key not in seen, "Duplicate task/run pair")
        seen.add(key)
        versions.add((row["skill_sha256"], row["dataset_sha256"]))
        groups.setdefault(row["task_id"], []).append(row["passed"])
    study.need(len(versions) == 1, "Do not pool different skill or dataset versions")
    return {"schema_version": 1, "run_kind": payload["run_kind"],
        "skill_sha256": next(iter(versions))[0], "dataset_sha256": next(iter(versions))[1],
        "outcomes_authenticated": False, "grader": "external_to_this_summary",
        "tasks": [{"id": task, "metrics": metrics(values, k)} for task, values in sorted(groups.items())],
        "interpretation": "Without-replacement estimates within each task's observed runs, not a guarantee for future tasks."}


def example_plan():
    return {"schema_version": 1, "study_id": "synthetic-001", "stages": [
        {"id": "design", "depends_on": [], "inputs": ["brief.md"],
         "required_artifacts": ["outline"], "review_mode": "separate_execution",
         "acceptance": [{"id": "coverage", "description": "Decision and measurement coverage"}]},
        {"id": "codebook", "depends_on": ["design"], "inputs": [],
         "required_artifacts": ["datamap"], "review_mode": "host",
         "acceptance": [{"id": "mapping", "description": "Variable mapping matches the design"}]}]}


def _prepare(root):
    root.mkdir()
    (root / "brief.md").write_text("Synthetic scope: fictional category decisions.\n")
    (root / "outline.md").write_text("Synthetic decision-to-measurement outline.\n")
    (root / "datamap.json").write_text('{"synthetic":true,"variables":["q1"]}\n')
    study.initialize(root, example_plan())


def _revision(root):
    return study.status(root)["revision"]


def _submit(root, sid="design"):
    study.start(root, sid, "synthetic-builder", _revision(root))
    artifact = {"id": "outline", "path": "outline.md"} if sid == "design" else {"id": "datamap", "path": "datamap.json"}
    study.submit(root, sid, [artifact], _revision(root))


def _review_payload(root, sid="design"):
    stage = next(s for s in study.status(root)["stages"] if s["id"] == sid)
    return {"candidate_sha256": stage["candidate_sha256"], "execution_id": "synthetic-reviewer",
        "criteria": [{"id": "coverage" if sid == "design" else "mapping", "verdict": "passed",
                      "reason": "Prewritten synthetic fixture; no semantic model review"}]}


def _finish(root, sid="design"):
    _submit(root, sid)
    study.review(root, sid, _review_payload(root, sid), _revision(root))
    study.complete(root, sid, _revision(root))


def _blocked(callback, reason):
    try:
        callback()
    except GateError as error:
        return reason in str(error)
    return False


def _case(root, name):
    _prepare(root)
    if name == "resume_and_complete":
        _finish(root); _finish(root, "codebook")
        return study.status(root)["complete"]
    if name == "dependency_blocks":
        return _blocked(lambda: study.start(root, "codebook", "synthetic-builder", 0), "Dependencies")
    _submit(root)
    payload = _review_payload(root)
    if name == "coverage_blocks":
        payload["criteria"] = []
        return _blocked(lambda: study.review(root, "design", payload, _revision(root)), "coverage")
    if name == "self_review_blocks":
        payload["execution_id"] = "synthetic-builder"
        return _blocked(lambda: study.review(root, "design", payload, _revision(root)), "different declared")
    study.review(root, "design", payload, _revision(root))
    if name == "stale_artifact_blocks":
        (root / "outline.md").write_text("Modified after review")
        return _blocked(lambda: study.complete(root, "design", _revision(root)), "Current complete")
    if name == "transitive_invalidation":
        study.complete(root, "design", _revision(root)); _finish(root, "codebook")
        (root / "brief.md").write_text("Changed business scope")
        return all(s["status"] == "stale" for s in study.status(root)["stages"])
    raise GateError("Unknown lifecycle scenario")


def run(output, repeats=3):
    study.need(type(repeats) is int and 1 <= repeats <= 20, "Use 1 to 20 repeats per scenario")
    output = Path(output)
    study.need(not output.exists(), "Evaluation output already exists")
    output.mkdir(parents=True)
    names = ["resume_and_complete", "dependency_blocks", "coverage_blocks", "self_review_blocks",
             "stale_artifact_blocks", "transitive_invalidation"]
    cases = []
    for name in names:
        outcomes, errors = [], []
        for index in range(repeats):
            try:
                passed = _case(output / f"{name}-{index + 1}", name)
                outcomes.append(passed)
                errors.append(None if passed else "unexpected_behavior")
            except Exception as error:
                outcomes.append(False)
                errors.append(type(error).__name__)
        cases.append({"id": name, "outcomes": outcomes, "errors": errors, "metrics": metrics(outcomes, repeats)})
    result = {"synthetic": True, "model_calls": 0, "semantic_quality_measured": False,
        "review_identity": study.IDENTITY_SCOPE, "scenarios": len(names), "repeats": repeats,
        "runs": len(names) * repeats, "passed_runs": sum(sum(c["outcomes"]) for c in cases),
        "all_runs_passed": all(all(c["outcomes"]) for c in cases), "cases": cases,
        "metric_scope": "Finite observed-run estimates; repeated deterministic fixtures do not measure model reliability."}
    (output / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result
