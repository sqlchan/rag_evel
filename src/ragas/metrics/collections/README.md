# Collections 指标总览

本目录包含 Ragas 的各类评估指标实现，每个子目录对应一种或一组相关指标，并配有独立的功能说明文档。

## 目录结构

| 子目录 | 说明 | 文档 |
|--------|------|------|
| **answer_accuracy** | 答案准确度（双评委 0/2/4 刻度） | [README](answer_accuracy/README.md) |
| **answer_correctness** | 答案正确性（陈述分解 + TP/FP/FN + 语义相似度） | [README](answer_correctness/README.md) |
| **answer_relevancy** | 答案相关性（反推问题 + 相似度 + 敷衍检测） | [README](answer_relevancy/README.md) |
| **agent_goal_accuracy** | 智能体目标准确度（有/无参考） | [README](agent_goal_accuracy/README.md) |
| **context_precision** | 上下文精确度（每条 context 有用性 + AP） | [README](context_precision/README.md) |
| **context_recall** | 上下文召回率（参考答案陈述是否可归因于 context） | [README](context_recall/README.md) |
| **context_relevance** | 上下文相关性（双评委） | [README](context_relevance/README.md) |
| **context_entity_recall** | 上下文实体召回（实体集合交集/参考实体） | [README](context_entity_recall/README.md) |
| **faithfulness** | 忠实度（陈述 + NLI 支持比例） | [README](faithfulness/README.md) |
| **factual_correctness** | 事实正确性（双向 claim 分解 + NLI，precision/recall/f1） | [README](factual_correctness/README.md) |
| **response_groundedness** | 回答 grounded 程度（双评委 0/1/2） | [README](response_groundedness/README.md) |
| **tool_call_f1** | 工具调用 F1（集合匹配） | [README](tool_call_f1/README.md) |
| **tool_call_accuracy** | 工具调用准确度（顺序 + 参数匹配） | [README](tool_call_accuracy/README.md) |
| **sql_semantic_equivalence** | SQL 语义等价 | [README](sql_semantic_equivalence/README.md) |
| **quoted_spans** | 引用片段对齐（规则） | [README](quoted_spans/README.md) |
| **summary_score** | 摘要得分（关键短语→问题→答案 + 简洁度） | [README](summary_score/README.md) |
| **topic_adherence** | 主题遵循（precision/recall/f1） | [README](topic_adherence/README.md) |
| **noise_sensitivity** | 噪声敏感度（相关/无关上下文下的错误率） | [README](noise_sensitivity/README.md) |
| **domain_specific_rubrics** | 领域定制 rubric（1–5 分） | [README](domain_specific_rubrics/README.md) |
| **instance_specific_rubrics** | 样本级 rubric | [README](instance_specific_rubrics/README.md) |
| **multi_modal_faithfulness** | 多模态忠实度（文本+图像） | [README](multi_modal_faithfulness/README.md) |
| **multi_modal_relevance** | 多模态相关性 | [README](multi_modal_relevance/README.md) |
| **chrf_score** | 字符级 CHRF 分数 | [README](chrf_score/README.md) |
| **datacompy_score** | 表格数据对比（CSV 行/列 precision/recall/f1） | [README](datacompy_score/README.md) |

## 公共基础

- **base.py**：`BaseMetric` 基类，继承 `SimpleBaseMetric` 与 `NumericValidator`，负责 LLM/Embedding 组件校验及 `ascore`/`score`/`batch_score` 的同步/异步封装。
- 各指标通常包含 `metric.py`（主逻辑）、`util.py`（Prompt 与数据结构）、`__init__.py`（导出）。

## 使用说明

- 需要 LLM 的指标需传入符合 `InstructorBaseRagasLLM` 的实例；需要 Embedding 的需传入符合 `BaseRagasEmbedding` 的实例。
- 各子目录下的 **README.md** 描述该指标的功能、核心步骤、依赖与示例用法；代码中的关键步骤已添加中文注释便于阅读。
