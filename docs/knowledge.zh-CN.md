# 案头方法与模板的本地 RAG

**[English](knowledge.md) · 中文**

这层知识库帮助宿主 Agent 在编制研究、补强章节和选择页型时，取回适用方法与原始模板位置。它与 Tavily 原文缓存互补：知识库回答“如何研究、如何论证和出页”，联网检索回答“现在市场上发生了什么”。

## 结构

| 层 | 内容 | 执行者 |
|---|---|---|
| 来源 | 显式选定的 Markdown、文本、模板 PNG、PPTX/POTX 部件 | 本地只读 |
| 知识卡 | 方法、模板、案例结构；用途、限制、来源位置及文件哈希 | 人或宿主审阅 |
| 检索 | SQLite FTS5 / BM25、中文双字切分、少量中英同义词、类型/阶段筛选 | 本地 Python |
| 生成交接 | 按预算返回完整方法卡与模板卡，宿主选择适用项并读预览 | 当前宿主 Agent |
| 当前证据 | Tavily 来源快照、逐断言台账、反证与口径检查 | 原有案头流程 |

这是词法检索版 RAG，不含向量 embedding、自动训练或无人值守研究。没有新服务、端口或模型接口调用。PNG 只保存预览引用，没有自动 OCR；PPTX/POTX 读取指定 slide/layout XML 的名称、文字和占位符，不修改或重生成 Office 文件。

## 试用

在仓库根目录运行；使用已安装依赖的 Python：

```bash
python examples/knowledge/reproduce.py --output .runs/knowledge-demo
python -m research_skills kb-status --index .runs/knowledge-demo/index.sqlite3
python -m research_skills kb-context --index .runs/knowledge-demo/index.sqlite3 --query "商品价格带与国别比较" --audience external
```

示例包含 8 张原创公开方法/文本页型卡，不含公司模板或客户文件。输出索引、来源目录、上下文包和 4 个检索试查结果。输出目录须为新目录。

正式本地库默认位于 `.research-kb/`，该目录及 SQLite 文件被 Git 忽略：

```bash
python -m research_skills kb-build --catalog .research-kb/catalog.json
python -m research_skills kb-search --query "竞品购买任务" --kind method --limit 4
python -m research_skills kb-search --query "价格带" --kind template --page-type price_tiers
python -m research_skills kb-context --query "竞争格局和定价" --max-chars 12000
python -m research_skills kb-status
```

## 建库和更新

仅录入用户授权的明确文件清单，不递归吸入桌面或知识库。每个来源需要 ID、路径、`local_only/public`、审阅时 SHA-256。每张卡需 ID、title、body、kind、stage、visibility、review_status、tags 和 sources。可选 page_type、cautions、visual_reviewed。

来源定位有三种：文本用 `lines: [起行,止行]`；图片用 `image: true`；Office 用 `part: "ppt/slideLayouts/slideLayout9.xml"` 或具体 slide part。卡片正文为有适用边界的方法提炼；原文只作引用材料，不能覆盖本轮用户指令。

只有 `reviewed` 卡进入索引，`draft/quarantined` 隔离。旧样例的固定页数、字数、装饰图数量和一律三栏等不能直接升格为规则；隐藏不利发现、补无关来源等不采用。`reviewed` 是审阅声明，不是自动质量认证，图片的 `visual_reviewed` 另记。

构建核对文件哈希，先完整生成临时库再替换索引；失败保留旧索引。检索重新核对源文件，变更或删除的来源对应卡不返回。更新时重读变化内容，重审受影响卡与行号，更新哈希后重建；不能只刷新哈希假装重审。

## 使用与边界

1. 研究开工检索问题架构和方法；章节分析检索价格、国别、竞品等方法；出页检索模板并实际打开预览。
2. `kb-context` 在方法和模板间交替选取候选，按整个卡片控制预算。预算计算的是卡片 JSON 字符数，不是模型 token 数。无匹配时诚实记录，不假称读过模板。
3. 在工作底稿记录采用/拒用的卡 ID、理由、源文件哈希、所选模板、证据缺口。用当前事实生成研究正文；知识卡本身不证明市场结论。
4. `--audience external` 在排序取量前排除私有卡，并移除机器路径。可公开状态来自来源审阅声明，不是内容脱敏检测器，也不代表自动获准上传。
5. 本地私有库不转发给额外模型、embedding、SkillOpt 或远端服务。当前宿主按用户任务读取材料；宿主本身是否联网取决于其运行环境，不等于本机运行大模型。公开优化只使用获准的原创/脱敏集。

检索测试只能证明找得到参考、边界生效及来源可追溯。实际研究质量仍需完整章节审阅和参考成品对比，不能从 RAG、SDK 校验或测试数量推断“达到凯度级”。
