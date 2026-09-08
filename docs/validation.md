# Validation record

Current package: 0.2.0, 2026-09-08. The v0.1.0 release remains a historical five-output bundle.

| Layer | Observed result |
|---|---|
| Python behavior tests | 38 passing local tests |
| Office demo | Original five outputs plus two survey/codebook outputs, Microsoft Open XML SDK: 0 errors |
| Refusal demonstration | Fabricated quote blocked; no final report created |
| Skill metadata | Seven skill entrypoints passed the skill-creator format validator |
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
