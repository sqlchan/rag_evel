# 可用指标列表

Ragas 提供一组评估指标，用于衡量 LLM 应用的性能。这些指标旨在帮助你客观度量应用表现，并覆盖不同应用与任务，如 RAG 与智能体工作流。

每个指标本质上都是为评估应用某一方面而设计的范式。基于 LLM 的指标可能进行一次或多次 LLM 调用来得到分数或结果。你也可以用 Ragas 修改或编写自己的指标。 

## 检索增强生成
- [上下文精确率](context_precision_zh.md)
- [上下文召回率](context_recall_zh.md)
- [上下文实体召回](context_entities_recall_zh.md)
- [噪声敏感度](noise_sensitivity_zh.md)
- [回答相关性](answer_relevance_zh.md)
- [忠实度](faithfulness_zh.md)
- [多模态忠实度](multi_modal_faithfulness_zh.md)
- [多模态相关性](multi_modal_relevance_zh.md)

## Nvidia 指标
- [答案准确率](nvidia_metrics_zh.md#answer-accuracy)
- [上下文相关性](nvidia_metrics_zh.md#context-relevance)
- [回答 grounded 程度](nvidia_metrics_zh.md#response-groundedness)

## 智能体或工具使用

- [主题遵循](agents_zh.md#topic-adherence)
- [工具调用准确率](agents_zh.md#tool-call-accuracy)
- [工具调用 F1](agents_zh.md#tool-call-f1)
- [智能体目标准确率](agents_zh.md#agent-goal-accuracy)

## 自然语言比较

- [事实正确性](factual_correctness_zh.md)
- [语义相似度](semantic_similarity_zh.md)
- [非 LLM 字符串相似度](traditional_zh.md#non-llm-string-similarity)
- [BLEU 分数](traditional_zh.md#bleu-score)
- [CHRF 分数](traditional_zh.md#chrf-score)
- [ROUGE 分数](traditional_zh.md#rouge-score)
- [字符串包含](traditional_zh.md#string-presence)
- [精确匹配](traditional_zh.md#exact-match)


## SQL

- [基于执行的 DataCompy 分数](sql_zh.md#execution-based-metrics)
- [SQL 查询等价性](sql_zh.md#sql-query-semantic-equivalence)

## 通用

- [方面批评](general_purpose_zh.md#aspect-critic) 
- [简单准则评分](general_purpose_zh.md#simple-criteria-scoring)
- [基于量表的评分](general_purpose_zh.md#rubrics-based-scoring)
- [实例级量表评分](general_purpose_zh.md#instance-specific-rubrics-scoring)

## 其他任务

- [摘要](summarization_score_zh.md)
