[English](README.md) · **中文**

# 北美生活方式零售研究示例

研究设计案例展示整体方案、定性指南、问卷与码表的交接。未执行实地研究，也没有市场发现。23页方案使用虚构品牌与设计假设，未包含真实客户、原始材料或受访者答案。

| 成品 | 内容 |
|---|---|
| [研究方案 Word](deliverables/research-plan.docx) | 定性与定量、样本、分析和排期 |
| [问卷 Excel](deliverables/questionnaire.xlsx) | 54节点，51道受访者题、3个系统节点 |
| [码表 Excel](deliverables/codebook.xlsx) | 120变量、长表Datamap、4套开放题框架 |
| [定性访谈指南](qualitative-guide.md) | 75分钟深访、60分钟陪访及交接 |
| [编程说明](programming-guide.md) | 基础与加样、显示及平台待验证项 |
| [分析计划](analysis-plan.md) | 指标、基数、缺失和比较口径 |

问卷为中文主稿，英语、法语和西语本地化尚未完成，不应直接上线招募。

## 复现

在仓库根目录按主README安装环境后执行：

```bash
python examples/north-america-retail/reproduce.py --output .runs/case-replay
```

重新生成两份Excel、验证随包方案Word，回放方案、问卷、码表三阶段并输出脱敏凭证。复用本轮已记录的审阅，不调用模型或重新研究。输入改动后需重新复核。重复执行须指定新的输出目录。

阅读 [复核边界](review-scope.md)，机器输入与路径用例见同目录JSON。
