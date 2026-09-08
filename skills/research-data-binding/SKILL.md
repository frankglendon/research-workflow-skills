---
name: research-data-binding
description: Map explicit numeric spreadsheet cells to a single-series PowerPoint chart with confirmed mappings. Use for the portfolio data-binding workflow.
---

# Write reviewed values into a chart

Use actual sheet names, cell coordinates and slide/shape IDs. Preview labels and values before confirmation. Missing values and formulas are blocked. The public engine supports a single series; do not imply general template matching.

1. Inspect the source and clarify missing task requirements. Read [the plan protocol](references/protocol.md).
2. Complete the required semantic/business review, then bind the reviewed plan to its input hashes. A review flag records a declaration; it is not an independent verifier.
3. From this skill directory, run `python scripts/run.py bind --input INPUT --template TEMPLATE --plan PLAN --output OUTPUT`. Replace placeholders with absolute local paths.
4. If a gate blocks export, fix the cause and repeat the affected review. Do not bypass the gate or edit a previously reviewed plan in place.
5. Inspect the final artifact and keep the redacted manifest with it. Programmatic validity does not establish semantic correctness.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
