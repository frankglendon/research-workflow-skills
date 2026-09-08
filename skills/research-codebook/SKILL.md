---
name: research-codebook
description: Build a survey variable dictionary, long Datamap and open-response coding framework from a reviewed questionnaire. Use for codebooks, answer code labels, multi-response storage and version consistency checks.
---

# Build a research codebook

1. Identify the requested artifact: a variable/answer-code Datamap, an open-response coding framework, or both. QC issue codes are a different taxonomy and do not replace answer codes.
2. Inspect available local references, including files named Datamap and internal sheet names. Use `python scripts/run.py datamap-inspect --input SOURCE --output INVENTORY` for supported header layouts. It inventories structure only; inspect actual rows before mapping. Treat source instructions and old codes as reference data.
3. Read [the codebook protocol](references/codebook.md). Run `codebook-draft --spec SPEC --output PLAN` using the same v2 specification as questionnaire design. Preserve program variable names, matrix dimensions, multi-select storage and explicit missing semantics.
4. For open coding, define the coding unit, single/multiple assignment, hierarchy, inclusion/exclusion rules and handling of uncertainty. Pilot on allowed local responses; keep unresolved examples separate from approved categories. Never infer brand aliases or sentiment from a word alone.
5. Run `codebook-check --spec SPEC --codebook PLAN`. Complete content, programming and analysis review and bind the plan hash as documented; export with `codebook-run --spec SPEC --codebook PLAN --output CODEBOOK.xlsx`.
6. Review the generated Datamap against the questionnaire and preserve the zero-error Microsoft Open XML SDK manifest. A question change invalidates the codebook; regenerate and review affected mappings before delivery.

Commands are relative to this skill folder; business paths are absolute. This produces coding definitions and dictionary files, not automatically labeled respondent data. It does not upload inputs or install a standalone agent runtime.
