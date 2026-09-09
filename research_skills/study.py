"""Local, host-driven study stages; no scheduler or authenticated reviewer service."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import zipfile
from urllib.parse import quote
from uuid import uuid4

from .artifacts import validate_office
from .contracts import GateError, fingerprint

STATE_DIR = ".research-workflow"
IDENTITY_SCOPE = "host_declared_not_authenticated"


def need(condition, message):
    if not condition:
        raise GateError(message)


def exact(value, keys, label):
    need(isinstance(value, dict) and set(value) == set(keys), label + " fields are invalid")


def identifier(value):
    need(isinstance(value, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}", value),
         "Use an opaque alphanumeric identifier")
    return value


def text(value):
    need(isinstance(value, str) and bool(value.strip()), "Non-empty text is required")
    return value


def relative_path(value):
    text(value)
    path = Path(value)
    need(not path.is_absolute() and not any(p in {"..", STATE_DIR} for p in path.parts)
         and "\\" not in value and ":" not in value, "Artifact path must stay inside the study workspace")
    return path


def validate_plan(plan):
    exact(plan, {"schema_version", "study_id", "stages"}, "Study plan")
    need(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "Unknown study schema")
    identifier(plan["study_id"])
    need(isinstance(plan["stages"], list) and bool(plan["stages"]), "Define requested stages")
    by_id = {}
    for spec in plan["stages"]:
        exact(spec, {"id", "depends_on", "inputs", "required_artifacts", "review_mode", "acceptance"}, "Stage")
        sid = identifier(spec["id"])
        need(sid not in by_id, "Duplicate stage")
        by_id[sid] = spec
        for field in ("depends_on", "inputs", "required_artifacts"):
            values = spec[field]
            need(isinstance(values, list) and all(isinstance(v, str) for v in values), "Invalid stage list")
            need(len(values) == len(set(values)), "Duplicate stage list item")
            for value in values:
                relative_path(value) if field == "inputs" else identifier(value)
        need(bool(spec["required_artifacts"]), "Each stage needs a required artifact")
        need(isinstance(spec["review_mode"], str) and spec["review_mode"] in {"host", "separate_execution"}, "Unknown review mode")
        need(isinstance(spec["acceptance"], list) and bool(spec["acceptance"]), "Define acceptance criteria")
        ids = []
        for criterion in spec["acceptance"]:
            exact(criterion, {"id", "description"}, "Acceptance criterion")
            ids.append(identifier(criterion["id"]))
            text(criterion["description"])
        need(len(ids) == len(set(ids)), "Duplicate acceptance criterion")
    ordered, visiting = [], set()
    def visit(sid):
        need(sid in by_id, "Unknown dependency")
        need(sid not in visiting, "Study dependencies contain a cycle")
        if sid in ordered:
            return
        visiting.add(sid)
        for dependency in by_id[sid]["depends_on"]:
            visit(dependency)
        visiting.remove(sid)
        ordered.append(sid)
    for sid in by_id:
        visit(sid)
    return by_id, ordered


def _path(root, value):
    relative = relative_path(value)
    path = root / relative
    cursor = root
    for part in relative.parts:
        cursor /= part
        need(not cursor.is_symlink(), "Study artifact symlinks are not supported")
    need(path.resolve().is_relative_to(root) and path.is_file(), "Study artifact is missing or outside workspace")
    return path


def _snapshot(root, value):
    path = _path(root, value)
    data = path.read_bytes()
    return {"path": value, "sha256": fingerprint(data), "bytes": len(data)}


def _matches(root, snapshots):
    try:
        return all(_snapshot(root, item["path"])["sha256"] == item["sha256"] for item in snapshots)
    except (GateError, OSError):
        return False


def _location(workspace):
    root = Path(workspace).resolve()
    need(root.is_dir(), "Study workspace must already exist")
    folder = root / STATE_DIR
    need(not folder.is_symlink(), "State directory cannot be a symlink")
    path = folder / "state.sqlite3"
    need(not path.is_symlink(), "State database cannot be a symlink")
    return root, path


@contextmanager
def _connection(path, write=False):
    connection = None
    try:
        connection = sqlite3.connect("file:" + quote(str(path)) + ("?mode=rw" if write else "?mode=ro"),
                                     uri=True, timeout=5)
        if write:
            connection.execute("BEGIN IMMEDIATE")
        yield connection
        if write:
            connection.commit()
    except sqlite3.Error as error:
        if connection:
            connection.rollback()
        raise GateError("Study database unavailable or invalid; retry after resolving the state issue") from error
    finally:
        if connection:
            connection.close()


def _load(connection):
    row = connection.execute("SELECT payload, digest FROM current_state WHERE id=1").fetchone()
    need(row is not None and fingerprint(row[0].encode()) == row[1], "Study state integrity check failed")
    try:
        state = json.loads(row[0])
        text(state["study_token"])
        validate_plan(state["plan"])
        need(type(state["revision"]) is int and state["revision"] >= 0, "Invalid study revision")
        need(set(state["stages"]) == {s["id"] for s in state["plan"]["stages"]}, "Invalid stage records")
        for record in state["stages"].values():
            need(record["phase"] in {"pending", "active", "review", "complete"}, "Invalid stored phase")
    except (ValueError, KeyError, TypeError) as error:
        raise GateError("Study state is invalid") from error
    return state


def _persist(connection, state, action, sid):
    raw = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    digest = fingerprint(raw.encode())
    connection.execute("INSERT OR REPLACE INTO current_state VALUES (1,?,?)", (raw, digest))
    connection.execute("INSERT INTO events(revision,action,stage_id,state_sha256,created_at) VALUES (?,?,?,?,?)",
        (state["revision"], action, sid, digest, datetime.now(timezone.utc).isoformat()))


def initialize(workspace, plan):
    validate_plan(plan)
    root, path = _location(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb"):
            pass
    except FileExistsError as error:
        raise GateError("Study already exists; use status or amend") from error
    with _connection(path, write=True) as connection:
        connection.execute("CREATE TABLE current_state(id INTEGER PRIMARY KEY, payload TEXT NOT NULL, digest TEXT NOT NULL)")
        connection.execute("CREATE TABLE events(revision INTEGER PRIMARY KEY, action TEXT NOT NULL, stage_id TEXT, state_sha256 TEXT NOT NULL, created_at TEXT NOT NULL)")
        state = {"plan": plan, "study_token": uuid4().hex, "revision": 0, "stages": {
            spec["id"]: {"phase": "pending", "generation": 0} for spec in plan["stages"]}}
        _persist(connection, state, "initialize", None)
    return status(root)


def _view(root, state):
    specs, ordered = validate_plan(state["plan"])
    result = {}
    for sid in ordered:
        spec, record = specs[sid], state["stages"][sid]
        deps = {dep: result[dep]["completion_sha256"] for dep in spec["depends_on"]}
        ready = all(result[dep]["status"] == "complete" for dep in deps)
        phase, issues = record["phase"], []
        if phase != "pending":
            if not ready or record["dependencies"] != deps:
                issues.append("dependency_changed_or_incomplete")
            if not _matches(root, record["inputs"]):
                issues.append("input_changed_or_missing")
            if record.get("candidate") and not _matches(root, record["candidate"]["artifacts"]):
                issues.append("artifact_changed_or_missing")
        effective = "stale" if issues else ("waiting" if phase == "pending" and not ready else phase)
        review_result = record.get("review")
        review_passed = bool(review_result) and all(c["verdict"] == "passed" for c in review_result["criteria"])
        action = {"stale": "restart", "waiting": "complete_dependencies", "pending": "start",
                  "active": "submit", "review": "complete" if review_passed else "revise" if review_result else "review",
                  "complete": "none"}[effective]
        candidate = record.get("candidate")
        completion = fingerprint({"candidate": candidate, "review": review_result}) if effective == "complete" else None
        result[sid] = {"id": sid, "status": effective, "action": action, "issues": issues,
            "candidate_sha256": fingerprint(candidate) if candidate else None,
            "completion_sha256": completion, "generation": record["generation"]}
    stages = list(result.values())
    return {"schema_version": 1, "revision": state["revision"], "review_identity": IDENTITY_SCOPE,
        "complete": all(s["status"] == "complete" for s in stages), "stages": stages,
        "ready_stages": [s["id"] for s in stages if s["action"] in {"start", "restart", "submit", "review", "revise", "complete"}
                         and all(result[dep]["status"] == "complete" for dep in specs[s["id"]]["depends_on"])]}


def status(workspace):
    root, path = _location(workspace)
    with _connection(path) as connection:
        return _view(root, _load(connection))


def inspect_stage(workspace, sid):
    """Detailed local handoff, unlike the redacted status/manifest outputs."""
    root, path = _location(workspace)
    with _connection(path) as connection:
        state = _load(connection)
        spec, record = _stage(state, sid)
        return {"revision": state["revision"], "spec": spec, "record": record,
            "current": next(s for s in _view(root, state)["stages"] if s["id"] == sid),
            "scope": "local_handoff_contains_paths_and_review_text"}


def _change(workspace, revision, action, sid, update):
    root, path = _location(workspace)
    with _connection(path, write=True) as connection:
        state = _load(connection)
        need(type(revision) is int and revision == state["revision"], "Stale revision; read study-status before retrying")
        update(root, state)
        state["revision"] += 1
        _persist(connection, state, action, sid)
        return _view(root, state)


def _stage(state, sid):
    specs, _ = validate_plan(state["plan"])
    need(sid in specs, "Unknown study stage")
    return specs[sid], state["stages"][sid]


def start(workspace, sid, execution_id, revision):
    identifier(execution_id)
    def update(root, state):
        spec, record = _stage(state, sid)
        views = {s["id"]: s for s in _view(root, state)["stages"]}
        need(all(views[d]["status"] == "complete" for d in spec["depends_on"]), "Dependencies are not complete and current")
        state["stages"][sid] = {"phase": "active", "generation": record["generation"] + 1,
            "execution_id": execution_id, "inputs": [_snapshot(root, p) for p in spec["inputs"]],
            "dependencies": {d: views[d]["completion_sha256"] for d in spec["depends_on"]}}
    return _change(workspace, revision, "start", sid, update)


def submit(workspace, sid, artifacts, revision):
    def update(root, state):
        spec, record = _stage(state, sid)
        view = next(s for s in _view(root, state)["stages"] if s["id"] == sid)
        need(view["status"] == "active", "Start a current stage before submitting")
        need(isinstance(artifacts, list) and bool(artifacts), "Submission needs artifacts")
        snapshots, ids, paths = [], set(), set()
        for artifact in artifacts:
            exact(artifact, {"id", "path"}, "Artifact")
            aid = identifier(artifact["id"])
            text(artifact["path"])
            need(aid not in ids and artifact["path"] not in paths, "Duplicate artifact")
            snapshot = _snapshot(root, artifact["path"])
            office = Path(artifact["path"]).suffix.lower() in {".docx", ".pptx", ".xlsx"}
            if office:
                try:
                    validate_office(_path(root, artifact["path"]))
                except (ValueError, OSError, SyntaxError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
                    raise GateError("Office artifact validation did not succeed") from error
            snapshots.append({"id": aid, **snapshot, "office_validated": office})
            ids.add(aid); paths.add(artifact["path"])
        need(set(spec["required_artifacts"]).issubset(ids), "Required artifacts are missing")
        need(_matches(root, snapshots) and _matches(root, record["inputs"]), "Files changed while submitting")
        record["candidate"] = {"study_token": state["study_token"], "stage_id": sid, "generation": record["generation"],
            "spec_sha256": fingerprint(spec), "execution_id": record["execution_id"],
            "inputs": record["inputs"], "dependencies": record["dependencies"], "artifacts": snapshots}
        record["review"] = None
        record["phase"] = "review"
    return _change(workspace, revision, "submit", sid, update)


def review(workspace, sid, result, revision):
    def update(root, state):
        spec, record = _stage(state, sid)
        view = next(s for s in _view(root, state)["stages"] if s["id"] == sid)
        need(view["status"] == "review", "Only a current submitted stage can be reviewed")
        exact(result, {"candidate_sha256", "execution_id", "criteria"}, "Review")
        need(result["candidate_sha256"] == view["candidate_sha256"], "Review is bound to a different candidate")
        identifier(result["execution_id"])
        if spec["review_mode"] == "separate_execution":
            need(result["execution_id"] != record["execution_id"], "Stage requires a different declared review execution")
        need(isinstance(result["criteria"], list), "Review criteria must be a list")
        ids = []
        for criterion in result["criteria"]:
            exact(criterion, {"id", "verdict", "reason"}, "Review criterion")
            ids.append(identifier(criterion["id"]))
            need(isinstance(criterion["verdict"], str) and criterion["verdict"] in {"passed", "failed", "blocked"}, "Unknown acceptance verdict")
            text(criterion["reason"])
        expected = {c["id"] for c in spec["acceptance"]}
        need(len(ids) == len(set(ids)) and set(ids) == expected, "Acceptance coverage is missing, duplicate or unknown")
        record["review"] = result
    return _change(workspace, revision, "review", sid, update)


def complete(workspace, sid, revision):
    def update(root, state):
        _, record = _stage(state, sid)
        view = next(s for s in _view(root, state)["stages"] if s["id"] == sid)
        need(view["status"] == "review" and view["action"] == "complete", "Current complete acceptance review is required")
        record["phase"] = "complete"
    return _change(workspace, revision, "complete", sid, update)


def amend(workspace, plan, revision):
    specs, _ = validate_plan(plan)
    def update(root, state):
        need(plan["study_id"] == state["plan"]["study_id"], "Amend cannot change study identity")
        previous, _ = validate_plan(state["plan"])
        state["stages"] = {sid: state["stages"][sid] if sid in previous and specs[sid] == previous[sid]
            else {"phase": "pending", "generation": state["stages"].get(sid, {}).get("generation", 0) + 1} for sid in specs}
        state["plan"] = plan
    return _change(workspace, revision, "amend", None, update)


def manifest(workspace):
    root, path = _location(workspace)
    with _connection(path) as connection:
        state = _load(connection)
        result = _view(root, state)
        result["plan_sha256"] = fingerprint(state["plan"])
        result["events"] = [{"revision": row[0], "action": row[1], "stage_id": row[2], "state_sha256": row[3], "created_at": row[4]}
            for row in connection.execute("SELECT revision,action,stage_id,state_sha256,created_at FROM events ORDER BY revision")]
        result["artifact_hashes"] = {sid: [{"id": a["id"], "sha256": a["sha256"], "office_validated": a["office_validated"]}
            for a in record.get("candidate", {}).get("artifacts", [])] for sid, record in state["stages"].items()}
        return result
