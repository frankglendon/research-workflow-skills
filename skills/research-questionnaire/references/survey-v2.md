# Questionnaire schema v2

Use repository `examples/survey-v2.json` as a **synthetic technical example**, never a ready-made client questionnaire. All business files use absolute paths. The package module `survey_design` is the executable contract.

| Field | Contract |
|---|---|
| `schema_version`, `meta.version` | `2` and an explicit study version |
| `meta`, `populations[].sampling` | Project, languages, timing and sampling assumptions; these are reviewed by the host, not statistically validated |
| `populations` | Unique portable `key`, readable `name`; every population has questions |
| `objectives` | Unique `id`, business `decision`, intended `metric`; every objective maps to questions |
| `qc_plan` | Project-specific pilot and quality plan; no universal timing/length cutoff |
| `questions` | `id`, `population`, `module`, `type`, `text`, `objective_ids` |
| `options` | Unique `code` and `label`; optional `kind`, `exclusive`, `fixed`, `specify` |
| `variable_names` | Optional canonical variable → existing export name map; preserve longitudinal identifiers |
| `routing_cases` | Synthetic answers with `id`, `population`, `answers`, `expected_visited`; all explicit routing/display branches must be covered before export |

Supported types: `single`, `dropdown`, `multi`, `nps`, `scale5`, `scale0_10`, `matrix`, `rank`, `open`, `numeric`. Choice types require options. Matrix requires `rows: [{code,label}]`. Multi requires integer `min_selections` and `max_selections`. Rank requires `rank_count`; answers are codes in rank order. Numeric requires finite `min` and `max`.

`kind` is `normal`, `other`, `none`, `dont_know`, or `not_applicable`. Multi non-substantive options are exclusive; `other` is not automatically exclusive. `specify: true` creates a separate text variable for single/multi/dropdown. `randomize: true` requires fixed special options. Codes are stable independently of presentation order.

## Explicit programming

- `show_if: [{question_id: "S1", codes: [1]}]` means all conditions must match; a condition matches any listed code. Only earlier selection questions are supported. A skipped prerequisite does not satisfy a condition.
- `routes: [{codes: [2], target: "END"}]` applies to the current answer. Targets must be later questions in the same population or `END`. If a multi answer matches different targets, simulation fails.
- `default` is `NEXT` (default) or `END`.
- `instruction` and `programming_note` are human-readable text. The engine **does not execute** these strings.
- Explicit loops, derived expressions and piping are blocked. Arbitrary predicates, survey-platform code generation, real quota management, other-text validation and complete fieldwork simulation are not implemented.

`survey-check` validates a draft without declaring it reviewed. `survey-simulate --cases FILE` compares reviewed expected paths. Export also evaluates the specification's `routing_cases`; coverage counts are a structural test, not proof of all possible answer combinations.

## Review binding

Only after content, programming and analysis review, set:

```json
{"review": {"status": "approved", "content": true, "programming": true,
 "analysis": true, "spec_sha256": "DIGEST"}}
```

`DIGEST = survey_design.spec_hash(spec)` is the canonical SHA256 of the complete specification excluding `review`. Hash calculation never performs a review. Any change to content, variables, cases or sampling invalidates it. The declaration is not cryptographic reviewer authentication or independent model verification.

## Exports and limits

`survey-run` exports Study, Sampling, Analysis plan, Questionnaire, Programming, Variables and Datamap sheets. Datamap has one answer code per row. Multi choices expand to 0/1 variables; 0 means eligible but not selected. Not-asked and missing states remain distinct and require a separate collection-time missing-reason field. Matrix and rank retain row/item codes. Preserve native survey-program names using `variable_names`.

The compiler does not estimate incidence, validate population representativeness, derive causal claims or certify question wording. These belong to study design and pilot review.
