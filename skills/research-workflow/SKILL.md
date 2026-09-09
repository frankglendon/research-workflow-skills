---
name: research-workflow
description: Coordinate a research brief across study design, desk research, questionnaires, codebooks, data QC and report delivery. Use when a request spans multiple research stages or needs a study handoff plan.
---

# Coordinate a research study

Act as the host's research lead. Use only the stages needed for the user's decision; a desk-only study does not require a questionnaire. This skill supplies coordination instructions, not another autonomous process or permission to spawn agents.

1. Record a concise local `study.json`: decision, scope, outputs, assumptions, budget/stop conditions, source inventory and stage status. Keep client content local. Existing user instructions control whether clarification is needed. For study classification, use [project types](references/project-types.md): primary/secondary business decisions, methods and scope are separate dimensions. Classify by objective, not by a single metric or file title.
2. Route to the seven professional skills below, load each only when needed, and preserve deliverable paths and content hashes in the study record. For a complete proposal or mixed-method outline, start with `research-study-design`. Types do not require separate agents. A study plan does not mean statistical estimation or fieldwork is implemented; record capability gaps. Inspect historical reference scope and role before reuse, and leave unresolved geography or entry-versus-expansion assumptions explicit.
3. For tracked multi-stage work, use the [persistent study commands](references/runtime.md). Keep the business brief separate from the executable plan; read status/inspect before resuming. Track only requested dependencies and concrete acceptance items. SQLite stores committed progress; current file hashes and upstream completions determine whether a stage remains valid. Use the returned revision for writes instead of manually editing state.
4. Review each handoff against its current upstream version. Questionnaire edits invalidate dependent codebooks and programming tests; source changes invalidate dependent claims. Require every acceptance item to pass before marking a tracked stage complete. A different declared execution ID is not authenticated reviewer identity, and an ID must never be invented to simulate a separate execution. Reuse unaffected work.
5. Close each requested stage with its actual result; retain draft, unresolved and failed work. The local state module is host-driven, not an unattended research runtime. Repeated lifecycle tests measure software behavior; model or artifact-quality comparisons require separately graded repeated runs with fixed skill/dataset versions.

| Stage | Skill | Handoff |
|---|---|---|
| Overall study design | `research-study-design` | Decision-to-method mapping, qualitative/quantitative design, sample and analysis plan, execution assumptions |
| Evidence and research | `research-evidence-report` | Research question, sources, claim ledger, narrative, open gaps |
| Questionnaire | `research-questionnaire` | v2 spec, analysis mapping, programming cases, questionnaire |
| Codebook | `research-codebook` | Same-spec variable dictionary, Datamap, optional open coding framework |
| Data quality | `research-survey-qc` | Reviewed findings and unchanged source data |
| Report data binding | `research-data-binding` | Confirmed source-to-chart mappings |
| Translation | `research-slide-translation` | Complete reviewed text units, protected numbers |

Drafting and checking may occur as separate passes in the same host. Do not describe this as independent model verification. Host planning, search, synthesis and semantic judgment are distinct from the package's deterministic checks.

See [handoffs and deployment choices](references/handoffs.md) when managing a full study.
