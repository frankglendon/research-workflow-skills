# Editable artifact authoring

These scripts use the configured `@oai/artifact-tool` JavaScript runtime. It is an authoring dependency supplied by the host environment, not installed by the Python package. The frozen Office files can be downloaded and validated without that authoring runtime.

1. Use a fresh writable build directory and copy `workbook-data.json`, `desk-research-content.json` and `sources.json` into it. Preserve the frozen delivery.
2. Make `@oai/artifact-tool` available through Node module resolution (for example, the host-configured `node_modules`). Use Node 24 and the matching artifact runtime. The recorded authoring run used the Hiragino Sans GB font; install an appropriately licensed compatible CJK font or revise the explicit design font and inspect the resulting layout.
3. Run `node authoring/render-workbooks.mjs /absolute/build-directory` for the two workbooks.
4. For PowerPoint set `PRESENTATIONS_SKILL_DIR` to the installed presentation skill directory containing `container_tools/artifact_tool_utils.mjs`, `ARTIFACT_PYTHON` to the absolute Python executable and `RUNTIME_NODE_MODULES` to the configured runtime module directory. Run `node authoring/render-desk.mjs /absolute/build-directory`.
5. Inspect every slide and each worksheet, then validate every final Office file with the repository's Microsoft Open XML SDK validator. The presentation authoring helper also checks native table/chart ownership, chart workbook packaging and layout geometry. It does not certify factual meaning.

After any authored content edit, perform a fresh content/programming/analysis review, bind the spec/codebook hashes and regenerate the review manifest. Never update a hash merely to bypass a failed review. The case verifier is an offline replay of a reviewed snapshot, not evidence of new semantic approval or live-source freshness.
