---
name: research-evidence-report
description: Build an editable PPT from reviewed claims bound to source excerpts. Use for a concise evidence report, with retrieval performed by the host.
---

# Build an evidence-backed report

Fetch sources with an available retrieval tool, retaining excerpts and scope. Exact quotation is necessary but does not prove entailment. Check units, time, population, negation and conflicting sources. The renderer only uses supported claim text; no unbound slide prose.

1. Inspect the source and clarify missing task requirements. Read [the plan protocol](references/protocol.md).
2. Complete the required semantic/business review, then bind the reviewed plan to its input hashes. A review flag records a declaration; it is not an independent verifier.
3. From this skill directory, run `python scripts/run.py research --plan PLAN --output OUTPUT`. Replace placeholders with absolute local paths.
4. If a gate blocks export, fix the cause and repeat the affected review. Do not bypass the gate or edit a previously reviewed plan in place.
5. Inspect the final artifact and keep the redacted manifest with it. Programmatic validity does not establish semantic correctness.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
