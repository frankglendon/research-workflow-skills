# Classify the decision before selecting tools

This is a working taxonomy for study planning, not an official proprietary methodology or a claim that every category has a dedicated implemented engine. Use it when a brief spans business questions or the user asks what kind of research is needed.

Choose a primary type from the decision the client will make. Add secondary types only for explicit supporting decisions. One metric or question does not define an entire project: an NPS item can appear in brand research, and a price item does not establish a pricing study. If the objective is unresolved, record `primary_type: null` and keep useful source inventory work moving.

| Type ID | Decision | Typical evidence or output | Check before claiming completion |
|---|---|---|---|
| `experience_loyalty` | Which customer experiences should improve? | Recommendation/satisfaction measures, journey pain points, improvement priorities | Define eligible customers, touchpoint and recall period; inspect bases and driver evidence |
| `brand_health` | Where is the brand gaining or losing strength? | Awareness/consideration/use funnel, image, barriers, tracking baseline | Comparable population, questions, periods and denominators; one wave is not a trend |
| `brand_positioning` | What should the brand stand for, and for whom? | Audience, functional/emotional value, differentiated positioning hypotheses | Separate proposed positioning from consumer-tested results |
| `segmentation` | Which distinct groups should the business prioritize? | Segment definitions, size evidence, profiles and targeting criteria | Separate assumed personas from validated segments; document method, stability and assignment rules |
| `usage_needs` | How, when and why is the category used? | Usage and attitudes (U&A), occasions, unmet needs and barriers | Distinguish buyer, user, occasion and current versus intended behavior |
| `product_innovation` | Which concept, feature or offer should progress? | Needs-to-feature mapping, concept/product/package test design, trade-offs | A needs interview is not a completed concept or product test; define stimuli and comparisons |
| `pricing_value` | What price, premium or offer mix should be considered? | Perceived value, price response, feature trade-offs and scenarios | Observed spend or stated willingness alone does not establish elasticity or an optimal price |
| `shopper_channel` | Where and how can purchase conversion improve? | Discovery-to-purchase journey, channel choice, retail/service benchmark | Separate consumer observation, self-report and desk evidence; avoid unmeasured conversion claims |
| `communications` | What message, campaign, IP or sponsorship should be used or evaluated? | Recognition, associations, response to creative, campaign evaluation | Exposure/recall alone does not prove causal lift or ROI; identify the evaluation design |
| `market_growth` | Which market, category or growth opportunity merits action? | Market boundaries, competitors, needs, opportunities and entry/expansion options | Recheck dates/geographies/source definitions; market size alone is not an attainable forecast |

## Keep independent dimensions separate

Record methods (`desk`, `qualitative`, `quantitative`, `observation`, `experiment`, `transactional_analysis`) separately from business types. These are possible methods, not an implemented feature list. Record cadence (`ad_hoc`, `tracking`, or `unknown`), sector, countries, target population, time horizon and deliverables separately. Cross-border research is a scope choice; it can contain brand, needs or experience work.

For each historical reference, retain its role (`brief`, `proposal`, `questionnaire`, `report`, `benchmark`, or `hypothesis`), location, and what was actually inspected. A file's presence does not prove the user delivered the project. Do not count duplicate versions as separate projects. A filename saying “two markets” is not evidence that both market instruments are present; inspect sheets and scope.

## Route only the work requested

| Requested work | Relevant skills | Boundary |
|---|---|---|
| Market/competitor assessment from existing sources | Evidence report | Preserve evidence gaps; do not invent survey results |
| Consumer questions or survey revision | Questionnaire, then codebook if a coded deliverable is needed | Primary-data collection requires its own execution plan |
| Historical questionnaire or Datamap review | Questionnaire or codebook, as relevant | Do not regenerate unrelated outputs |
| Collected response quality | Survey QC with the correct variable definitions | QC is a delivery stage, not a business research category |
| Existing tables into a report or report translation | Data binding or slide translation | No implied statistical analysis engine |
| Segmentation, pricing, concept tests or causal campaign evaluation | Relevant planning and design skills; record execution gaps | Dedicated statistical estimation, fieldwork, experimentation and effect measurement are not implemented by these six skills |

Select actual skill names from the entrypoint's stage table. Do not create a new skill or agent for every project type. Specialized statistical work may later justify its own tested capability when real inputs and acceptance criteria are available.

## Study record

The host may extend its existing `study.json` with `classification_version`, `decision`, `classification` (primary/secondary type and rationale), `methods`, `scope`, `reference_roles`, `requested_stages`, `capability_gaps` and `unresolved`. See [a synthetic planning record](study.example.json). This is an example convention, not a new validated CLI schema or automatic router.

When a retailer asks about North America, preserve that stated region and leave country coverage unresolved unless specified. Verify existing operations before deciding whether the business question is first entry or expansion. Historical single-country material informs hypotheses; it does not supply current multi-country findings. If the user says a fuller brief will follow, prepare the inventory and scope gaps without starting a self-assigned full study.
