# Optional SkillOpt evaluation

The adapter targets a single public `SKILL.md` and reviewed synthetic tasks. It disables transcript harvesting, memory evolution and automatic adoption. Run it against a compatible local [SkillOpt checkout](https://github.com/microsoft/SkillOpt).

```bash
python -m research_skills.optimize --engine /path/to/SkillOpt \
  --skill research-survey-qc --backend mock --dry-run
python -m research_skills.optimize --engine /path/to/SkillOpt \
  --skill research-survey-qc --backend codex
```

The real backend requires a logged-in Codex CLI and consumes the user's model allowance. Execute skills serially. The adapter records the effective replay label, skill/data hashes, validation scores and final test evidence. State remains in ignored local directories.

Each public skill has six synthetic decision scenarios: two train, two validation, two test. The judge checks a decision label, not reasoning quality or actual artifact behavior. A positive case must state all prerequisites; otherwise a correct request for review can be falsely scored as failure.

Read `report.md` and the staged diff before proposing adoption. Require validation improvement with no per-case regression, inspect final test results and rerun the repository's behavior tests. A still-reviewed single-target proposal can be adopted from the SkillOpt checkout with `python -m skillopt_sleep adopt --project /path/to/research-workflow-skills --staging /exact/staging/RUN --legacy`. Do not use a default latest staging directory across multiple skills. Adoption preserves existing-target backups.

The public edition has **mock integration checks only** at release. It does not inherit model evaluation scores from another implementation. No model training or unattended optimization is claimed.

Compatibility note: this adapter uses SkillOpt's Python API, which may change. It was checked against a local checkout based on `bdfdc30a8e17309c06cdbe8449f01bdecc120203` with local modifications. The external engine is not bundled; a clean upstream checkout at that revision alone is not claimed to reproduce the exact integration environment.
