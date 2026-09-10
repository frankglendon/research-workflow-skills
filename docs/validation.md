# Validation record

## Tavily-first retrieval — 0.4.0, 2026-09-09

84 behavior tests passed locally, including 19 retrieval checks: one outstanding request, deduplication, persisted retry/budget limits, source/snippet separation, wrong-URL and cross-workspace responses, atomic failed imports, source hashes, Firecrawl markdown normalization, exact candidate offsets, redacted summaries and actual CLI resumption/no-overwrite behavior. The synthetic three-response demonstration makes no network/model calls and refuses an unreviewed ledger.

The host ran three actual Tavily calls through the request/record workflow: one search returned no results, one known-page extraction failed, and a selected official examples page was extracted and retrieved locally. All outcomes remain recorded. Earlier interface lookups are separate setup calls. Firecrawl has fixture checks only. These checks do not measure web coverage or research accuracy. Detailed results: [retrieval validation](retrieval-validation.json).

SkillOpt's new six-case retrieval dataset passed public mock integration, with no adopted edit. Private model scores are not public evaluation. The included case artifacts were generated with 0.3.0; 0.4.0 also recompiles the workbooks and validates the frozen proposal successfully.

## Complete design case — 2026-09-09

The fictional North American retail case contains a 23-page Word proposal and two Excel workbooks: 54 questionnaire nodes (51 respondent questions and 3 system fields), 120 variables and 4 open coding frames. All three files pass Microsoft Open XML SDK validation with 0 errors. The proposal pages and all 11 workbook sheets were visually inspected. Twelve synthetic routing cases cover 56 explicit branches in the supported compiler; this does not test a survey platform's live randomization.

The case replay validates frozen input hashes, recompiles both workbooks and completes three scoped design milestones using recorded host reviews. It calls no model, conducts no fieldwork and does not authenticate an independent reviewer. CI runs this replay alongside the existing tests and demos. The case files were authored on engine 0.3.0; `case-study-v1` also bundles the subsequent 0.4.0 retrieval code. The case files themselves were not used as SkillOpt tasks.

Current package: 0.4.0, 2026-09-09. The v0.1.0 release remains a historical five-output bundle.

| Layer | Observed result |
|---|---|
| Python behavior tests | 84 passing local tests |
| Office demo | Original five outputs plus two survey/codebook outputs, Microsoft Open XML SDK: 0 errors |
| Refusal demonstration | Fabricated quote blocked; no final report created |
| Skill metadata | Eight skill entrypoints passed the skill-creator format validator |
| SkillOpt | Original five mock checks plus new questionnaire/codebook/coordinator mock dry-runs; no adopted edits |
| CI | See the public Tests workflow for the independent Linux run |

Local environment: Python 3.12, macOS, .NET 10 and DocumentFormat.OpenXml 3.1.0. Tested Python dependency versions are in `constraints-py312.txt`. The CI setup uses the .NET 10 channel and immutable action commit IDs.

The tests cover missing/duplicate review coverage, stale plan edits, fabricated quotes, changed claim text, false review strings, protected translation numbers, unconfirmed bindings, actual cell-to-chart values, invalid jump targets, input preservation, no-overwrite behavior, source changes during export, redacted manifests, and failed Office validation leaving no final output.

All fixture content is synthetic. Source URLs in the example ledger are illustrative and are not retrieved by the demo. Prewritten reviews make file behavior reproducible without a model; they are not evidence that an agent performed a semantic review. PNG previews are rendered from these synthetic outputs. LibreOffice rendering is used only for layout inspection; Microsoft's SDK is the schema authority.

## Limits of the evidence

- These are contract and artifact checks, not measured accuracy on real surveys, research or translations.
- The public workflow scope is narrower than a general business automation product: one chart series, three-column QC, a structured ten-type questionnaire compiler and slide text runs.
- There is no independent reviewer authentication, semantic entailment model, online provenance verification, recovery service or autonomous research loop.
- Plan and evidence hashes can detect changes; an untrusted actor can still fabricate an entirely new reviewed plan. Authorization belongs to the host/system boundary.
- The checked public SkillOpt integration used mock replay; no private implementation's scores are imported into this release.
- Dependency setup and runtime behavior on Windows require its own environment verification; the instructions are provided without claiming Windows Office UAT.

## Survey/codebook checks

Added checks cover stale questionnaire/codebook review hashes, objective/population references, reserved option exclusivity, forward route targets and branch coverage, conflicting multi-answer routes, matrix/rank expansion, variable-name collisions, codeframe definitions/cycles and formula-like question text. The demo contains 7 synthetic questions, 13 variables and 2 routing paths. Three Datamap header layouts can be inventoried; arbitrary import, live programming, automatic open-response coding and unattended research remain outside the executable scope.

## Study-design increment — 2026-09-09

The package now has eight skill entrypoints: one coordinator and seven specialists, with six executable file engines. All eight skill formats, reference links and evaluation JSON files passed validation; 38 behavior tests passed locally. A broken desk-skill handoff reference was corrected. The new study-design skill passed a mock SkillOpt integration run with no adopted edit. Study quality, fieldwork and statistical execution were not evaluated by these checks. No client proposal or historical material is included. The v0.2.0 demonstration bundle remains unchanged.

## Persistent-stage increment — 2026-09-09

65 behavior tests passed locally, including persisted resumption, atomic rollback after an injected write failure, revision conflicts, cycle/path/symlink rejection, invalid Office input, missing/failed acceptance items, changed inputs/artifacts, plan changes, cross-study review replay and transitive invalidation. A subprocess test exercises actual CLI status and refusal behavior.

The lifecycle demo ran six scenarios three times in distinct workspaces: **18/18 expected outcomes**, zero model calls, prewritten synthetic reviews. This checks deterministic behavior, not semantic quality or model reliability. The original Office workflows continue to pass the regression suite. The release does not regenerate or replace historical demo bundles.

The additional SkillOpt lifecycle dataset has six reviewed synthetic cases with 2/2/2 training/validation/test splits. The public package completed mock integration only, with no adopted edits. The adapter now marks failed/empty real model calls as invalid evaluation, omits their quality scores and exits with an error; those failures must not be interpreted as poor skill performance.

## Local knowledge retrieval — 2026-09-11, 0.7.0

116 tests passed locally. Sixteen new checks cover source locators, CJK/English retrieval, stale-source suppression, atomic failed rebuilds, public/private classification, external-audience filtering, whole-card budgets and CLI integration. The original eight-card demo passed four targeted retrieval smoke checks without network or model calls; it also runs in CI.

The implementation is SQLite FTS5 lexical retrieval with host generation handoff. These tests do not evaluate complete report quality or establish a SkillOpt improvement. No private corpus, template or index is distributed. See the [knowledge protocol](knowledge.md).
