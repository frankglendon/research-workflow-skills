# Reviewed plan protocols

Generate inspectable examples with `python -m research_skills demo --output .runs/demo`. Input workbooks, templates and all five plans appear under `.runs/demo/inputs/`. Synthetic review declarations in that command are fixture data, not model output.

All plans require `reviewed: true`. `review_sha256` equals `research_skills.contracts.fingerprint(payload)`, where `payload` is the complete plan excluding `review_sha256`. For file-based tasks, `input_sha256` is an ordered list of SHA-256 digests of file bytes. If a source or plan changes, perform the affected review again before creating a new digest. This protocol detects stale contents; it does not authenticate a human reviewer.

| Command | Input order | Required task payload |
|---|---|---|
| `qc` | Survey XLSX | `reviews`: unique Excel row numbers and `clean`/`issue`/`uncertain` verdicts; header exactly `id, score, comment` |
| `research` | No file inputs | `ledger.documents` and `ledger.claims`; exact source excerpts, hashes, scope and semantic-review declaration |
| `bind` | Metrics XLSX, template PPTX | `target.slide` (zero-based), `target.shape_id`, `series_name`, `entries` with `sheet`, `cell`, `label`, `confirmed` |
| `questionnaire` | No file inputs | `questions` with unique `id`, `type` (`single`, `open`, `nps`), `text`, options (`code`, `label`) and `jump_targets` |
| `translate` | Source PPTX | `translations`, keyed by the IDs returned by `translation-units` |

The evidence ledger schema is demonstrated in `research_skills/demo.py`. Documents have `id`, HTTP(S) `url`, `text` and `sha256`. Claims have `id`, `statement`, `status: supported`, `scope`, `evidence` (`document_id`, `quote`), `evidence_sha256`, `reviewed_statement_sha256`, and `semantic_reviewed: true`. Source hashes use UTF-8 text bytes; list/object hashes use the canonical JSON fingerprint helper.

## Operational boundaries

- Binding supports one numeric series. Blank, non-finite and formula cells block export; there is no inferred matching or formula evaluator.
- QC uses a public three-column fixture and a 0–10 score range. It is not a general survey-cleaning methodology.
- Questionnaire validation checks explicit target existence, not execution of natural-language route conditions or reachability.
- Translation covers slide XML text runs. It preserves other package parts, except deterministic chart axis repair if required. It does not translate notes, images, chart caches or embedded workbooks.
- Evidence reports render supported claim text directly. Quotes and numeric tokens constrain the output but do not verify online source authenticity or full meaning.
- Output paths must be new. Keep runtime plans in a local task directory and pass absolute paths when calling a skill script.

## Optional study lifecycle

The [stage protocol](../skills/research-workflow/references/runtime.md) adds a separate schema-versioned DAG plan, local SQLite checkpoints and candidate-bound acceptance review. It does not reinterpret the earlier free-form `study.example.json` as executable configuration. The synthetic runtime plan is a minimal example, not a required sequence for all studies.
