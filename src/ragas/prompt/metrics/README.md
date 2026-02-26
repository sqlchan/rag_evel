# Ragas Prompt Metrics 模块说明

本目录包含 **各评估指标** 使用的 prompt：既有面向 Instructor/结构化输出的 **BasePrompt 子类**（在 `base_prompt.py`），也有与 V1 行为一致的 **纯函数式 prompt**（返回拼好的字符串），供不同评估流水线调用。

## 文件与职责

| 文件 | 功能概要 |
|------|----------|
| **base_prompt.py** | 指标用结构化 Prompt 基类：to_string、_generate_examples、adapt（多语言翻译）。 |
| **common.py** | 通用 prompt 函数：statement_generator_prompt（将答案拆成陈述）、nli_statement_prompt（基于上下文的陈述忠实度 NLI）。 |
| **answer_accuracy.py** | 答案准确性双裁判：answer_accuracy_judge1/2_prompt，输出 0/2/4 分 JSON。 |
| **answer_correctness.py** | 答案正确性分类：correctness_classifier_prompt，输出 TP/FP/FN 分类与理由。 |
| **answer_relevance.py** | 答案相关性：answer_relevancy_prompt，生成反推问题 + 是否 noncommittal(0/1)。 |
| **context_relevance.py** | 上下文相关性双裁判：context_relevance_judge1/2_prompt，输出 0/1/2 分 JSON。 |
| **context_recall.py** | 上下文召回：context_recall_prompt，判断答案每句是否可归因于 context，输出 classifications。 |
| **context_entity_recall.py** | 上下文实体召回：extract_entities_prompt，从文本抽取唯一实体列表。 |
| **factual_correctness.py** | 事实正确性：claim_decomposition_prompt，按 atomicity/coverage 将回答分解为可验证 claims。 |
| **noise_sensitivity.py** | 噪声敏感度：nli_statement_prompt（与 common 中 NLI 逻辑一致，语句忠实度 0/1）。 |
| **response_groundedness.py** | 响应 groundedness 双裁判：response_groundedness_judge1/2_prompt，输出 0/1/2 分。 |
| **summary_score.py** | 摘要评分流水线：extract_keyphrases_prompt、generate_questions_prompt、generate_answers_prompt。 |

## 使用方式

- **函数式**：直接调用各 `*_prompt(...)`，得到完整 prompt 字符串，再交给 LLM 与解析逻辑。
- **BasePrompt**：若指标需要结构化输入/输出与多语言 adapt，可继承 `metrics.base_prompt.BasePrompt`，实现 instruction、input_model、output_model、examples，并复用其 to_string / _generate_examples / adapt。

更多细节见各同名 `.md` 文件（如 base_prompt.md、common.md 等）。
