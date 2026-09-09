# Optional SkillOpt evaluation

## 2026-09-09 study classification update

The coordinator gained a ten-type business taxonomy and scope/capability guidance. A mock dry-run reused the unchanged six-case dataset: baseline 0.0, candidate 0.0, gate reject, zero edits, zero adoptions and zero sessions. This checks adapter integration only; it is not a model evaluation of the new classification guidance and does not establish improved classification accuracy.

The adapter targets a single public `SKILL.md` and reviewed synthetic tasks. It disables transcript harvesting, memory evolution and automatic adoption. Run it against a compatible local [SkillOpt checkout](https://github.com/microsoft/SkillOpt).

```bash
python -m research_skills.optimize --engine /path/to/SkillOpt \
  --skill research-survey-qc --backend mock --dry-run
python -m research_skills.optimize --engine /path/to/SkillOpt \
  --skill research-survey-qc --backend codex
```

The real backend requires a logged-in Codex CLI and consumes the user's model allowance. Execute skills serially. The adapter records the effective replay label, skill/data hashes, validation scores and final test evidence. State remains in ignored local directories.

Each public skill has six synthetic decision scenarios: two train, two validation, two test. The judge checks a decision label or explicit judgment fields, not reasoning quality or actual artifact behavior. A positive case must state all prerequisites; otherwise a correct request for review can be falsely scored as failure.

Read `report.md` and the staged diff before proposing adoption. Require validation improvement with no per-case regression, inspect final test results and rerun the repository's behavior tests. A still-reviewed single-target proposal can be adopted from the SkillOpt checkout with `python -m skillopt_sleep adopt --project /path/to/research-workflow-skills --staging /exact/staging/RUN --legacy`. Do not use a default latest staging directory across multiple skills. Adoption preserves existing-target backups.

The public edition has **mock integration checks only** at release. It does not inherit model evaluation scores from another implementation. No model training or unattended optimization is claimed.

Compatibility note: this adapter uses SkillOpt's Python API, which may change. It was checked against a local checkout based on `bdfdc30a8e17309c06cdbe8449f01bdecc120203` with local modifications. The external engine is not bundled; a clean upstream checkout at that revision alone is not claimed to reproduce the exact integration environment.

## Version 0.2

New questionnaire, codebook and coordinator datasets each have six synthetic cases (2 train, 2 validation, 2 test). Mock dry-runs completed, with no proposals adopted and no claim of a model-quality score. The QUESTIONNAIRE and CODEBOOK datasets contain a known REVIEW/BLOCK taxonomy ambiguity for incomplete prerequisites; do not infer semantic accuracy from their regex labels. A future evaluation should separate permission to deliver from the next workflow action and introduce new unseen test cases.

## Study-design increment — 2026-09-09

Added `research-study-design` and a new six-case synthetic dataset with 2/2/2 splits. Boolean/count fields distinguish draft readiness, fieldwork approval, subset counting, boost/base denominators, assumed segments and sales causality. A mock dry-run completed with zero edits and zero adoptions. This verifies adapter wiring only; no private model scores or client proposal content are imported. Existing holdout cases were not relabeled.

## Lifecycle dataset and replay validity (0.3.0)

`evals/study-lifecycle-v1.json` adds six synthetic stage decisions with explicit boolean fields. The original datasets and holdout labels remain unchanged. Select it explicitly:

```bash
python -m research_skills.optimize --engine /path/to/SkillOpt \
  --skill research-workflow --dataset evals/study-lifecycle-v1.json --backend mock --dry-run
```

Only reviewed synthetic datasets inside `evals/` are accepted, including resolved symlink checks. Real Codex replay requires successful, non-empty model-call evidence; failed or empty calls invalidate evaluation and clear quality scores. Mock replay remains an integration check, never a quality score. A new dataset version cannot establish improvement against an earlier dataset.

For repeated externally graded runs, use `study-eval-summary`; keep task IDs, skill/dataset hashes and failures. At least one success among k and all k succeeding answer different questions. Neither a deterministic 18/18 check nor a small synthetic model score measures professional study quality.
