---
name: research-questionnaire
description: Design a structured research questionnaire, analysis mapping and programming specification with survey logic checks. Use for screening, scales, multi-choice, matrices, ranking and questionnaire revisions.
---

# Draft a structured questionnaire

Map business decisions to metrics and questions before drafting. Identify the population, screening criteria, sampling assumptions, languages, timing and pilot plan. Learn structure from authorized local references without inheriting client content or fixed project parameters.

1. Read [schema v2](references/survey-v2.md). Review wording for one concept per question, an explicit recall period, balanced labels and non-overlapping categories. Preserve existing scale definitions when comparability matters.
2. Keep unprompted awareness ahead of prompted lists. Distinguish not-asked, unknown, inapplicable and substantive zero. Special codes are project-defined; Other is not automatically exclusive. Randomization changes display order, never stored codes.
3. Run `python scripts/run.py survey-check --spec SPEC`. Add synthetic routing cases and run `survey-simulate --spec SPEC --cases CASES`. The simulator covers explicit forward routes and display conditions, not arbitrary prose or a live survey platform.
4. Review content, programming and analysis; bind the current specification hash and run `survey-run --spec SPEC --output OUTPUT`. Missing routing branch coverage or stale reviews block export.
5. Use `research-codebook` to generate the matching Datamap. Check variable names, multi-response storage, matrix dimensions and missing rules; then inspect Office validity and layout.

Do not invent incidence rates or quotas. Review marginal quota totals separately per dimension. Calibrate timing and quality rules through a pilot; do not assume one cutoff fits every study. Business review and fieldwork piloting remain required beyond the compiler checks.

The original small `questionnaire --plan PLAN` workflow remains supported through [its legacy protocol](references/protocol.md). Prefer v2 for new studies.

This skill requires the shared Python package installed from this repository. It does not run a web server or grant authority to publish or message anyone.
