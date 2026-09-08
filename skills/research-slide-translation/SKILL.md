---
name: research-slide-translation
description: Translate PPTX slide text runs with complete unit coverage and protected numeric tokens. Use for the public slide-text translation workflow.
---

# Translate reviewed slide text

Extract translation-units before translating. Review fidelity, negation and terms; preserve numeric tokens exactly. Notes, chart caches, image text and embedded workbooks are outside this public workflow. Review wrapping visually after export.

1. Inspect the source and clarify missing task requirements. Read [the plan protocol](references/protocol.md).
2. Complete the required semantic/business review, then bind the reviewed plan to its input hashes. A review flag records a declaration; it is not an independent verifier.
3. From this skill directory, run `python scripts/run.py translate --input INPUT --plan PLAN --output OUTPUT`. Replace placeholders with absolute local paths.
4. If a gate blocks export, fix the cause and repeat the affected review. Do not bypass the gate or edit a previously reviewed plan in place.
5. Inspect the final artifact and keep the redacted manifest with it. Programmatic validity does not establish semantic correctness.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
