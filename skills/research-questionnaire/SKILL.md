---
name: research-questionnaire
description: Design and validate a small questionnaire with single-choice, open and NPS questions and explicit jump targets. Use for the public questionnaire workflow.
---

# Draft a structured questionnaire

Resolve the research brief before drafting. Keep IDs and option codes unique; express jump targets explicitly and review their conditions separately. NPS has the full 0-10 scale. The static validator does not simulate routing or sampling design.

1. Inspect the source and clarify missing task requirements. Read [the plan protocol](references/protocol.md).
2. Complete the required semantic/business review, then bind the reviewed plan to its input hashes. A review flag records a declaration; it is not an independent verifier.
3. From this skill directory, run `python scripts/run.py questionnaire --plan PLAN --output OUTPUT`. Replace placeholders with absolute local paths.
4. If a gate blocks export, fix the cause and repeat the affected review. Do not bypass the gate or edit a previously reviewed plan in place.
5. Inspect the final artifact and keep the redacted manifest with it. Programmatic validity does not establish semantic correctness.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
