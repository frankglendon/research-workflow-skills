# Codebook protocol

The questionnaire uses [schema v2](../../research-questionnaire/references/survey-v2.md). `codebook-draft` derives `variables` deterministically, binds `questionnaire_sha256`, and sets a draft review. Never treat a generated draft as an approved coding scheme.

The plan has `schema_version: 1`, explicit `version`, `questionnaire_sha256`, `variables`, `codeframes`, and `review`. Changing the questionnaire or variable mapping requires regenerating the draft. Do not hand-edit derived variables; put export-name changes in the questionnaire's `variable_names` map.

Each optional open-response frame contains:

- `population`, `question_id`: an existing open question; one frame per question.
- `unit`: `response` or `meaning_unit`; retain source response linkage locally when segmenting.
- `mode`: `single` or `multi`. Different aspects in one answer can need multiple codes.
- `codes`: unique `code`, `label`, `definition`, `include`, `exclude`, optional `parent`. Parent chains must exist and be acyclic. A code is not defined by its short label alone.
- Optional `special: true` requires `exclusive: true`, distinguishing no answer, do not know and uninterpretable content as appropriate. Empty/invalid is not automatically a negative opinion. Specify which non-leaf categories are grouping labels in the coding instructions.

Keep positive/negative examples, rare categories, disagreements and pilot revisions locally. Frequency is not a sufficient reason to merge distinct meanings. Freeze code IDs after agreement; use a versioned change map when recoding. The current engine validates definitions and exports the framework; it does not perform automatic coding, adjudication or inter-coder reliability calculations.

For export, complete the same `review` structure as schema v2 with `spec_hash(plan)`, excluding its review field. Both questionnaire and codebook reviews are required. The workbook contains Version, Variables, long Datamap and Open coding sheets.

`datamap-inspect` recognizes long Question ID / Variable ID / Answer Code tables, Fields / Label / Type metadata and three-column value-label tables. It returns a source hash, sheet/header locations and column inventory without guessing conversions. Nested field metadata, loop indices, hidden variables, multiple-response mentions and formulas still need explicit mapping. An unfamiliar layout must not be silently converted.
