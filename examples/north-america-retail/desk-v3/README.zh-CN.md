[English](README.md) · **中文**

# MINISO 北美案头研究 v3

围绕需求、竞争与国家适配重做的商业案头报告。它替代 v2 案头部分作为当前案例入口；v2 问卷和码表继续保留。

- [可编辑报告](deliverables/desk-research.pptx)：52页，其中42页实质分析，13张原生图表、37张原生表格。
- [文字版](desk-research.zh-CN.md)、[来源](sources.json)、[商业问题与答案](research-map.json)、[编辑复核](editorial-review.zh-CN.md)。
- 覆盖8个外部竞品案例、美加墨差异、商品价格样本和反向证据。检索日期2026年9月9—10日。

报告采用公开事实与原创解释，无客户原件、原始答卷或机构背书。三国同款价格实测、细分市场规模和单店投资回报仍需补充证据。

## 本地重放

完成仓库安装后，在仓库根目录执行：

```sh
python examples/north-america-retail/desk-v3/reproduce.py --output outputs/desk-v3-replay
python -m research_skills desk-audit --study examples/north-america-retail/desk-v3/research-map.json
```

重放检查哈希、正文、引用、原生对象、柱图零基线及微软Open XML有效性（含图表工作簿），再复制到新目录。它不重新联网，不替代编辑与视觉审阅，不开展实访或外部SkillOpt回放。

## 编辑与渲染

编辑 `desk-research-content.json` 并维护口径和断言引用。`authoring/render.mjs` 使用宿主当前的 `@oai/artifact-tool` 演示文稿运行时。通过已安装演示文稿技能解析 `PRESENTATION_SKILL_DIR`、`RUNTIME_PYTHON`、`RUNTIME_NODE_research_skillsS`，让脚本可访问该Node依赖，再以提供的Node执行脚本并指定新输出目录。制作及校验沿用宿主技能。更新文件后先复核新版本，不为通过检查直接改写审阅哈希。

商品图与商标归原权利人，本案例用于研究说明。[图片来源](assets/image-source.json)。代码许可不转移第三方图片权利。

SkillOpt增加了六个章节语义评估任务。本轮仅完成本地mock dry-run，外部回放被自动审批拦截，未取得真实模型评分或采用优化候选。
