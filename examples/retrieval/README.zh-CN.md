[English](README.md) · **中文**

# 检索流程演示

在已安装环境的仓库根执行：

```bash
python examples/retrieval/reproduce.py --output .runs/retrieval-demo
```

脚本回放三份合成响应：Tavily 搜索、Tavily 取正文、显式选择 Firecrawl 取单页。网络和模型调用均为 0，无需配置 MCP。输出本地来源库、带原文位置的候选片段及脱敏凭证；未复核台账会被最终证据门禁拒绝。

真实 MCP 调用由宿主完成，见 [检索交接说明](../../skills/research-evidence-report/references/retrieval.md)。本演示中的 URL 和来源内容均为虚构。
