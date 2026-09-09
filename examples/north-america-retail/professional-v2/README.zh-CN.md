[English](README.md) · **中文**

# 专业研究交付包 v2

本版将整体方案落实为完整中文问卷、同版本码表和独立案头研究。内容独立撰写，不含历史客户原件或受访者数据。

| 交付物 | 内容 |
|---|---|
| [问卷 XLSX](deliverables/questionnaire.xlsx) | 104个节点：100个受访者题目、4个系统节点；7个工作表 |
| [码表 XLSX](deliverables/codebook.xlsx) | 520个回答变量，9个事前开放编码框架，缺失原因与指标分母 |
| [案头研究 PPTX](deliverables/desk-research.pptx) | 35页，4张原生图表、14张原生表格，12份公开来源、20条事实断言 |
| [编程交接](programming-guide.md)、[分析口径](analysis-plan.md)、[定性指南](qualitative-guide.md) | 从业务问题到执行、分析及定性定量衔接 |

问卷使用虚构品牌；案头报告中的真实公司与数据保留公开出处，不把企业事实改写成虚构品牌业绩。本案例不代表客户委托、品牌背书或已完成实访。[质量复核表](quality-review.md)记录对照维度，不能用题量或校验通过率替代专业内容判断。

## 离线复核

在已安装依赖的仓库根目录执行 `python examples/north-america-retail/professional-v2/reproduce.py --output .runs/professional-v2-replay`。需要Python及Microsoft .NET 10。复核输入哈希、问卷/码表绑定、22条合成完整回答路径与137个声明分支、全部工作簿单元格、原生表图、内嵌数据簿及Office结构，再复制已制作的成品到新目录。

这不是重新生成版式，也不重复执行来源检索、语义/视觉审阅或实地工作。重新制作见[作者说明](authoring/README.md)；冻结内容在workbook-data.json与desk-research-content.json，完整出处和断言定位在sources.json与claims.json，第三方原文不随包分发。

## 当前交付状态

这是中文研究及编程主稿。美加墨本地语言审校、正式调查平台联调、认知访谈和软启动尚未完成；设计估时30–38分钟，深度路径可能超过40分钟，必须试访后调整。现有模拟器不执行实际随机、配额、拒答/中断或回退恢复。原始v1保留在上级目录；v2问卷和码表必须配套，题号、时长和缺失规则以v2为准。
