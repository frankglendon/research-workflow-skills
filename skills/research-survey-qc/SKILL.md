---
name: research-survey-qc
description: Review a three-column survey workbook and export an audit sheet while preserving input cells. Use for the portfolio survey QC workflow.
---

# Review survey response quality

Require exactly id, score, comment columns. Review every populated row, keeping uncertain distinct from clean. The demo score range is 0-10; do not generalize it to other scales.

1. Inspect the source and clarify missing task requirements. Read [the plan protocol](references/protocol.md).
2. Complete the required semantic/business review, then bind the reviewed plan to its input hashes. A review flag records a declaration; it is not an independent verifier.
3. From this skill directory, run `python scripts/run.py qc --input INPUT --plan PLAN --output OUTPUT`. Replace placeholders with absolute local paths.
4. If a gate blocks export, fix the cause and repeat the affected review. Do not bypass the gate or edit a previously reviewed plan in place.
5. Inspect the final artifact and keep the redacted manifest with it. Programmatic validity does not establish semantic correctness.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
