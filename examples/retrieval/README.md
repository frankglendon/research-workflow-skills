**English** · [中文](README.zh-CN.md)

# Retrieval contract demonstration

Run from the installed repository root:

```bash
python examples/retrieval/reproduce.py --output .runs/retrieval-demo
```

The script replays three synthetic responses: Tavily discovery, Tavily page extraction and an explicitly selected Firecrawl page extraction. It makes **zero network/model calls** and needs neither MCP server. It writes a local source corpus, exact-text candidates and a redacted manifest. An unreviewed source ledger must be refused by the final-evidence contract.

For real host MCP execution, see [the retrieval handoff](../../skills/research-evidence-report/references/retrieval.md). Source URLs and content in this demonstration are fictional.
