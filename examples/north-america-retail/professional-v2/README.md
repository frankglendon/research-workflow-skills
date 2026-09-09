**English** · [中文](README.zh-CN.md)

# Professional research pack v2

A complete Chinese questionnaire master, linked codebook and a standalone public-source desk research report. This is an independently authored research-design case; it contains no historical client documents or field responses.

| Deliverable | Contents |
|---|---|
| [Questionnaire](deliverables/questionnaire.xlsx) | 104 nodes: 100 respondent questions plus 4 system nodes; 7 worksheets |
| [Codebook](deliverables/codebook.xlsx) | 520 answer variables, 9 prospective open-coding frames, missing reasons and analysis bases |
| [Desk research](deliverables/desk-research.pptx) | 35 editable slides, 4 native charts, 14 native tables, 12 public sources and 20 factual claims |
| [Programming](programming-guide.md) / [Analysis](analysis-plan.md) / [Qualitative guide](qualitative-guide.md) | Implementation rules, statistical boundaries and qualitative-to-quantitative handoff |

The desk report uses real public-company disclosures with dates and geographic qualifications. The questionnaire uses fictional brands; public financial facts are never relabeled as fictional-brand results. Neither represents commissioned client work or completed fieldwork. Benchmark review is documented in [quality-review.md](quality-review.md); it is not institutional certification.

## Verify the frozen delivery

From the repository root after installation, run `python examples/north-america-retail/professional-v2/reproduce.py --output .runs/professional-v2-replay`. Python and Microsoft .NET 10 are required. The check verifies hashes, questionnaire/codebook binding, 22 synthetic complete-answer paths covering 137 declared branches, every workbook cell against its dataset, native slide objects, embedded chart workbooks and Office schema validity. It copies the already-authored files to a new directory; it does not regenerate their layout or repeat semantic/visual review, source retrieval or fieldwork.

## Authoring and release status

`workbook-data.json` and `desk-research-content.json` are the authored content datasets. [Authoring instructions](authoring/README.md) explain how to regenerate editable files using the configured artifact runtime. Exact visual reproduction requires compatible fonts and runtime versions. Sources and claims include original links, scope, retrieval dates and locator hashes; full third-party source text is not distributed.

This is a Chinese design master. US English, Canadian English/French and Mexican Spanish review, production survey integration, cognitive interviews and a soft launch remain pending. Estimated burden is 30–38 minutes and may exceed 40 on deep paths; it has not been timed in fieldwork. The simulator does not execute actual randomization, panel quotas, refusal/breakoff or backward navigation.

The earlier v1 case remains available in the parent directory for historical reproduction. Use v2 questionnaire and codebook together; v2 supersedes v1 instrument wording, question IDs, timing estimates and missing-value conventions.
