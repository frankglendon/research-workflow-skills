# Handoffs and deployment choices

Keep one study brief and stable artifacts, rather than diverging copies of business context. Useful local stages are `brief`, `study_design`, `evidence`, `design`, `codebook`, `fieldwork`, `quality`, `report`, `delivery`. Record `not_requested`, `draft`, `review`, `complete`, `partial` or `blocked`, current upstream hashes, artifact paths and unresolved decisions. This is a host-maintained record, not an implemented background scheduler.

## Overall study design

For a full proposal, call `research-study-design` after interpreting the brief. Connect business decisions, qualitative exploration, quantitative validation, sample bases, analysis and delivery. Preserve unresolved assumptions; a reviewable draft is not fieldwork approval. Hand the frozen measurement design to the questionnaire skill. An isolated file task does not require a full proposal.

## Desk research loop

Plan deduplicated questions and queries first. Search with tools available in the host, prefer original sources, fetch only necessary pages and persist each result immediately. Follow host/user provider and rate-limit preferences. Revisit a query only for an identified evidence gap; cap queries/rounds according to the study budget. An exhausted budget leaves a visible gap, never an invented conclusion.

Separate raw source text, extracted observations, supported claims, inference and recommendations. Validate quotes and compare dates, units, denominator, geography and counterevidence. A source URL alone does not support an assertion. Repeated syndication is not independent corroboration. After each research round, update the gap register and determine whether more retrieval can change the decision.

The public evidence renderer currently makes claim/evidence slides from a provided ledger. It does not independently search, generate a full narrative, or construct a market study. The host can conduct those steps using the skill instructions, but the package's offline demo does not test them.

## Survey handoff

Research hypotheses become questions only when primary data can resolve them. Specify the analysis base for each question, screening and sample definitions, and known feasibility gaps. Preserve authorized historical export names when useful. Questionnaire and Datamap share one v2 specification hash. A confirmed codebook is a dependency for mapping collected columns into QC or analysis.

Do not convert a coding framework into a quality-deletion rule. “Not sure” can be a valid response; malformed output, respondent uncertainty, content negativity and irrelevant answers are different findings.

## When to split agents

Start with one host agent and seven focused skills. Skills are easy to revise, reuse and test; a single host keeps versions consistent. The cost is dependence on host tools/context and no independent background operation.

Split an evidence specialist or questionnaire-programming specialist into another agent only when it has a bounded input, separate permissions/budget, inspectable output and a measurable benefit from parallel work or independent checking. Separate agents add scheduling, retries, state reconciliation and integration testing. Multiple names or roles alone do not establish independence or quality.

For unattended operation, add a real runtime later: provider interfaces, persisted state machine, budget accounting, retry/cancellation, approval boundaries and integration tests. The existing compilers and gates can be reused. Choose that deployment after testing representative real tasks; do not build another platform merely to display agents.
