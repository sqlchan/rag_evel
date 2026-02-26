# metrics/common.py 功能说明

## 概述

存放 **多个指标共用** 的 prompt 函数，与 V1 的 PydanticPrompt.to_string() 输出保持一致，保证评估结果可比。当前包含：**陈述生成**（答案拆句）、**NLI 陈述忠实度**（基于上下文对每条陈述打 0/1）。

## 函数说明

### statement_generator_prompt(question, answer) -> str

- **作用**：给定问题和答案，要求 LLM 将答案中的每个句子拆成一条或多条“可独立理解、无代词的陈述”，输出 JSON 含 "statements" 数组。
- **用途**：Faithfulness、Answer Correctness 等指标的第一步——先把答案标准化为陈述列表，再与 ground truth 或 context 做 NLI/分类。
- 输入经 json.dumps 转义后嵌入模板；Schema 与示例与 V1 一致。

### nli_statement_prompt(context, statements) -> str

- **作用**：给定 context 和 statements 列表，要求对每条 statement 判断“是否可由 context 直接推断”，输出每条 verdict 0/1 及 reason。
- **用途**：Faithfulness、Noise Sensitivity 等——判断模型输出中的陈述是否忠于给定上下文。
- 输入经 json.dumps 格式化后嵌入；Schema 与示例与 V1 一致（NLIStatementOutput，含 StatementFaithfulnessAnswer 的 statements 数组）。
