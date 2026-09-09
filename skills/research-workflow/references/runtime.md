# Persistent study stages

Use these commands for a study spanning stages or requiring later resumption. A single-file request can still use its existing file engine directly. This optional module governs tracked stage completion; it does not intercept every legacy export, run models, schedule work or perform fieldwork.

Keep the business brief in the existing local `study.json`. Create a separate plan using [the synthetic plan](runtime-plan.example.json), including only requested stages. Do not overwrite or silently import an earlier free-form study record.

## Plan and local files

- Each stage has an opaque ID, dependencies, workspace-relative input paths, required artifact IDs, acceptance criteria and a review mode. Dependencies form a DAG, not a compulsory research sequence.
- Each acceptance item has a stable ID and a concrete description. Include measurement coverage, sampling bases, evidence, interpretation and visual review where relevant to the actual deliverable.
- `host` means a declared host review. `separate_execution` additionally requires distinct declared builder/reviewer execution IDs. Neither mode authenticates identities or proves independent model reasoning. Never invent a new ID to simulate a separate execution.
- Inputs and submitted artifacts must be regular files within the chosen workspace; symlinks, parent traversal and state-file artifacts are rejected. External source files remain covered by their original engine checks; a reference inventory does not automatically monitor external files.
- `.research-workflow/state.sqlite3` contains local paths, criteria and review explanations. Keep it local and out of Git. `study-status` and `study-export` omit these fields; use opaque IDs so metadata itself does not disclose clients.

## Commands

Use `python -m research_skills` followed by:

| Command | Required arguments | Effect |
|---|---|---|
| `study-init` | `--workspace DIR --plan FILE` | Create a new study, refuse overwrite |
| `study-status` | `--workspace DIR` | Read current phases, detected staleness, next actions and revision |
| `study-inspect` | `--workspace DIR --stage ID` | Read the detailed local stage handoff, current artifacts and acceptance items |
| `study-start` | `--workspace DIR --stage ID --execution ID --revision N` | Begin/restart with current inputs and dependencies; old downstream completions become stale |
| `study-submit` | `--workspace DIR --stage ID --artifacts FILE --revision N` | Hash a candidate; run Microsoft validation for DOCX/PPTX/XLSX |
| `study-review` | `--workspace DIR --stage ID --review FILE --revision N` | Record every criterion against the exact current candidate |
| `study-complete` | `--workspace DIR --stage ID --revision N` | Complete only after current dependencies, artifacts and passing review |
| `study-amend` | `--workspace DIR --plan FILE --revision N` | Revise the requested plan; reset changed stages, preserve unaffected work |
| `study-export` | `--workspace DIR --output FILE` | Write a new redacted status, hashes and event manifest |

Mutation revisions come from the most recent status/inspect response. A conflicting revision fails; reread state and reconcile the change, without blindly retrying a write. SQLite commits state and its event in one transaction. An interrupted write returns to the last committed checkpoint. A corrupt/uninitialized database is an explicit recovery issue; do not delete it and claim the prior study was recovered.

Artifact JSON is an array such as `[{"id":"outline","path":"outline.md"}]`. Review JSON has `candidate_sha256` from status, a real declared `execution_id`, and `criteria`: one `{id, verdict, reason}` per expected acceptance ID. Verdicts are `passed`, `failed` or `blocked`; explanations must be non-empty. Missing, duplicate, unknown or stale reviews cannot complete a stage.

Read status before resuming. Inspect the current stage, use its existing artifacts, and perform the returned action. On `stale`, restart the earliest affected stage and regenerate/review dependent work as needed. On `revise`, repair the stated failed items; there is no automatic retry loop. Budget and user scope still govern how much work to undertake. Never set a human-facing milestone to complete merely because a draft file exists.

## Repeated evaluation

`study-demo --output DIR --repeats 3` runs six synthetic lifecycle scenarios in 18 distinct workspaces. Reviews are prewritten, model calls are zero, and success measures expected completion/refusal behavior. It does not measure research quality.

`study-eval-summary --results FILE --k N --output FILE` summarizes externally graded runs. The input uses `schema_version: 1`, `run_kind` (`deterministic_fixture`, `model_replay` or `human_reviewed_artifact`), and `runs`. Each run supplies opaque `task_id`/`run_id`, `skill_sha256`, `dataset_sha256` and a boolean `passed`. For one comparison, keep skill and dataset versions fixed; each task needs at least k observed runs. Errors/timeouts must be retained as failed outcomes. Do not omit failed tasks or relabel holdout cases.

It reports the observed single-run pass rate, an at-least-one-success estimate, an all-k-success estimate and the literal all-runs-passed flag. The estimates use sampling without replacement within observed runs. They are not guarantees for future tasks. This summary trusts declared outcomes and neither grades artifacts nor authenticates the external evaluator.

SkillOpt remains the candidate proposal/evaluation tool. Use repeated outcomes as additional evidence, preserve untouched holdouts, and adopt only an actually improved candidate through its existing adoption path. A small synthetic score or repeated deterministic pass is not a measured gain in research quality.
