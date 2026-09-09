# Retrieval integration (0.4.0)

The evidence skill now uses a local retrieval journal around the host's installed MCP tools. Tavily is the default for both search and extraction. Firecrawl is retained as an explicit single-page markdown adapter. No extra model, server or provider configuration is required by this module.

| Previously | Now |
|---|---|
| Retrieval instructions only | Executable request reservations, persisted state and bounded retry/call limits |
| Manually collected source text | Provider response normalization, per-page snapshots, URLs and content hashes |
| Re-reading whole saved pages | Local BM25 candidate chunks with original-text offsets |
| Manual gap tracking | Explicit gap labels on planned and added jobs, deduplication and resumable status |

The host still decomposes research questions, chooses useful pages, issues MCP calls, reviews meaning and decides whether evidence is sufficient. Search snippets and generated summaries cannot enter the extracted-page index. A candidate relevance score cannot approve a claim. No independent reviewer authentication or embedding model is implemented.

Start with the [host handoff](../skills/research-evidence-report/references/retrieval.md) or [synthetic runnable example](../examples/retrieval/README.md). The source is [retrieval.py](../research_skills/retrieval.py); [behavior tests](../tests/test_retrieval.py) exercise restart, budgets, failure handling and source boundaries.

## Design references

The request/source-corpus/gap-driven loop was informed by the user's reference [production-deep-research-agent at revision 86fa709](https://github.com/DJAndrew0611/production-deep-research-agent/tree/86fa70982660037bb9292d87d8e811673ae6e818). The implementation here was written for this host/skill architecture; no upstream source code, custom MCP transport, Firecrawl deep-research runtime or embedding dependency was copied. In particular, an aggregate research answer is never assigned to several source URLs as if it were each page's text.

Tool routing was checked against [Tavily MCP documentation](https://docs.tavily.com/documentation/mcp), the available host tool schemas and the official [Firecrawl MCP server](https://github.com/firecrawl/firecrawl-mcp-server). Host prefixes can differ. Firecrawl support has synthetic adapter validation only; it was not live-connected in this environment.
