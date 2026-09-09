**English** · [中文](README.zh-CN.md)

# MINISO North America desk research, v3

A rebuilt commercial desk study answering demand, competition and country-adaptation questions. It replaces the desk portion of v2 as the current case; the v2 questionnaire and codebook remain available.

- [Editable report](deliverables/desk-research.pptx): 52 slides, including 42 substantive analysis pages, 13 native charts and 37 native tables.
- [Readable report](desk-research.zh-CN.md), [sources](sources.json), [business questions and answers](research-map.json), and [editorial review](editorial-review.zh-CN.md).
- Eight external competitor cases, US/Canada/Mexico differences, price examples and counterevidence. Sources were retrieved on September 9–10, 2026.

The report uses public facts and authored interpretations. It does not contain client originals or respondent data and has no agency or brand endorsement. Matched-country price audits, segment sizing and store investment returns remain outside the available evidence.

## Reproduce the frozen files

After repository setup, run from the repository root:

```sh
python examples/north-america-retail/desk-v3/reproduce.py --output outputs/desk-v3-replay
python -m research_skills desk-audit --study examples/north-america-retail/desk-v3/research-map.json
```

The first command checks hashes, narrative, evidence binding, native objects, explicit zero bar baselines and Microsoft Open XML validity, including chart workbooks. It copies the checked files to a new folder. It does not rerun retrieval, editorial or visual judgment, fieldwork or SkillOpt.

## Edit and render

Edit `desk-research-content.json`, retaining scope and claim references. `authoring/render.mjs` uses the host's current `@oai/artifact-tool` presentation runtime. Resolve `PRESENTATION_SKILL_DIR`, `RUNTIME_PYTHON` and `RUNTIME_NODE_MODULES` through the installed presentation skill, make the supplied Node packages available to the authoring script, and run it with the supplied Node executable and a new output directory. Follow that skill's authoring and validation workflow. Do not change a reviewed manifest just to suppress a failed check; review the new revision first.

Product photograph and trademarks belong to their respective owners and are used for the case analysis. [Photo attribution](assets/image-source.json). Code licensing does not transfer third-party image rights.

After explicit user authorization, real Codex replay completed: validation 1/2 (mean rubric score 0.875) and held-out test 1/2 (0.750). No edits were proposed or adopted; no optimization gain was demonstrated. See the [evaluation record](skillopt-evaluation.json). These six short chapter-review tasks do not certify a complete report or source entailment; the judge received the rubric and answer.
