**English** · [中文](README.zh-CN.md)

# A reproducible method-to-page handoff

Run `python examples/knowledge/reproduce.py --output .runs/knowledge-demo` from the repository root. The output includes a local index, eight original cards, four retrieval smoke checks and `context.json`. No company template, historical client content, model call or web request is used.

For a pricing task, the returned `method-price` card establishes the comparison fields and sample boundary. `template-price` supplies an original text layout recipe. The host can then draft a page with sampled item, specification, country, local price, observation date and conditions, plus an interpretation tied to actual collected evidence. The knowledge cards do not supply current prices or establish a price advantage.

This example demonstrates reference retrieval and generation handoff. It is not a completed market report or a measured improvement in research quality. For real tasks, record adopted card IDs, source hashes and evidence gaps, then obtain and review current sources.
