# Validation record

Release candidate: 0.1.0, 2026-09-08.

| Layer | Observed result |
|---|---|
| Python behavior tests | 20 passing local tests |
| Office demo | Five generated outputs, Microsoft Open XML SDK: 0 errors |
| Refusal demonstration | Fabricated quote blocked; no final report created |
| Skill metadata | Five skills passed the skill-creator format validator |
| SkillOpt | Five mock dry-runs completed; no quality improvement claim or adopted edits |
| CI | See the public Tests workflow for the independent Linux run |

Local environment: Python 3.12, macOS, .NET 10 and DocumentFormat.OpenXml 3.1.0. Tested Python dependency versions are in `constraints-py312.txt`. The CI setup uses the .NET 10 channel and immutable action commit IDs.

The tests cover missing/duplicate review coverage, stale plan edits, fabricated quotes, changed claim text, false review strings, protected translation numbers, unconfirmed bindings, actual cell-to-chart values, invalid jump targets, input preservation, no-overwrite behavior, source changes during export, redacted manifests, and failed Office validation leaving no final output.

All fixture content is synthetic. Source URLs in the example ledger are illustrative and are not retrieved by the demo. Prewritten reviews make file behavior reproducible without a model; they are not evidence that an agent performed a semantic review. PNG previews are rendered from these synthetic outputs. LibreOffice rendering is used only for layout inspection; Microsoft's SDK is the schema authority.

## Limits of the evidence

- These are contract and artifact checks, not measured accuracy on real surveys, research or translations.
- The public workflow scope is narrower than a general business automation product: one chart series, three-column QC, a small question-type set and slide text runs.
- There is no independent reviewer authentication, semantic entailment model, online provenance verification, recovery service or autonomous research loop.
- Plan and evidence hashes can detect changes; an untrusted actor can still fabricate an entirely new reviewed plan. Authorization belongs to the host/system boundary.
- The checked public SkillOpt integration used mock replay; no private implementation's scores are imported into this release.
- Dependency setup and runtime behavior on Windows require its own environment verification; the instructions are provided without claiming Windows Office UAT.
