**English** · [中文](README.zh-CN.md)

# North America retail study design example

A delivered design case connecting mixed-method planning, interviewing, a questionnaire and its versioned codebook. No fieldwork or consumer findings are claimed. Documents are Chinese masters; English, French and Spanish localization remains pending.

| Deliverable | Contents |
|---|---|
| [Study plan](deliverables/research-plan.docx) | Qualitative and quantitative methods, sampling and delivery |
| [Questionnaire](deliverables/questionnaire.xlsx) | 54 nodes: 51 respondent questions and 3 system nodes |
| [Codebook](deliverables/codebook.xlsx) | 120 variables, long Datamap and 4 open coding frames |
| [Qualitative guide](qualitative-guide.md) | Interviews, shopalongs and quantitative handoff |
| [Programming](programming-guide.md) | Routes, sample layers and remaining platform checks |
| [Analysis plan](analysis-plan.md) | Decisions, bases, NPS and concept comparisons |

## Reproduce

Install from the repository root, then run:

```bash
python examples/north-america-retail/reproduce.py --output .runs/case-replay
```

The script recompiles two workbooks, validates the included host-authored Word plan, and replays the recorded three-stage handoff. Fixed reviewed inputs and zero model calls. It does not conduct research, authenticate reviewers or certify fieldwork readiness. Use a fresh output directory. See the [review scope](review-scope.md).
