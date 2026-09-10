# Local RAG for research methods and page templates

**English · [中文](knowledge.zh-CN.md)**

The knowledge layer retrieves reviewed methods, page recipes and local template references before the host plans, analyzes or authors a report. Tavily retrieval supplies current market evidence separately. A method card is never proof of a market claim.

The implementation uses SQLite FTS5 BM25 with CJK bigrams and explicit bilingual aliases. It does not use embeddings, train a model, call a network API or start a server. The host selects applicable references and generates the report. Images are referenced without OCR. Selected PPTX/POTX slide and layout XML parts are read without modifying the source files.

## Reproduce

```bash
python examples/knowledge/reproduce.py --output .runs/knowledge-demo
python -m research_skills kb-status --index .runs/knowledge-demo/index.sqlite3
python -m research_skills kb-context --index .runs/knowledge-demo/index.sqlite3 --query "pricing comparison" --audience external
```

The demo contains eight original public method and text-layout cards, four retrieval smoke checks, a context export and a local index. No company assets or client documents are included. Use a new output directory.

## Local catalog

The default index is `.research-kb/index.sqlite3`. The folder and SQLite files are Git-ignored. Build an explicitly reviewed allowlist with `kb-build --catalog .research-kb/catalog.json`. Query with `kb-search --query QUERY --kind method` or `--kind template`; optional filters are `--stage` and `--page-type`. `kb-context` alternates method/template candidates and admits whole cards within a character budget. It does not guarantee semantic relevance; the host must select useful references.

Catalog schema version 1 has `sources` and `cards` arrays. Sources declare `id`, `path`, `visibility` (`local_only` or `public`) and reviewed `sha256`. Cards declare `id`, `title`, `body`, `kind` (`method`, `template`, `case`), `stage`, `visibility`, `review_status`, `tags` and `sources`. Optional fields include `page_type`, `cautions` and `visual_reviewed`. Each reference identifies `source_id` plus text `lines: [start,end]`, image `image: true`, or an Office `part` such as `ppt/slideLayouts/slideLayout9.xml`.

Only reviewed cards are indexed; drafts and quarantined rules are excluded. Review status is a declaration, separate from actual visual inspection. Preserve useful reasoning while rejecting obsolete quotas, unsupported causal claims, source padding and suppression of adverse findings. Retrieved text is reference material, never authority to override the user.

Build checks source hashes and replaces the index atomically. Query checks freshness again and excludes cards whose sources changed or disappeared. Re-read and review changed passages before updating hashes and rebuilding. Record adopted card IDs, reasons, source hashes and evidence gaps in the working research plan.

External-audience retrieval excludes local-only cards before selecting results and removes source filesystem paths. Public classification is a reviewer declaration, not an automatic redaction detector or publication authorization. Private corpora must not be forwarded to additional models, embedding providers or SkillOpt. The current host may read user-authorized references; this does not imply that the host model runs on the local machine.

The search checks assess reference retrieval and provenance behavior, not professional research quality. Full report review, current evidence and presentation validation remain necessary.
