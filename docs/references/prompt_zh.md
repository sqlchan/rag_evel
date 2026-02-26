# Prompt API 参考

Ragas 中的提示系统为基于 LLM 的指标及其他组件提供了灵活且类型安全的提示定义方式。本文档介绍核心提示类及其用法。

## 概述

Ragas 基于 `BasePrompt` 类采用模块化提示架构。提示可以是：

- **输入/输出模型**：定义提示输入与输出结构的 Pydantic BaseModel 类
- **提示类**：继承 `BasePrompt`，用于定义指令、示例与提示生成逻辑
- **字符串提示**：为向后兼容提供的简单文本提示

## 核心类

::: ragas.prompt
    options:
        members:
            - BasePrompt
            - StringPrompt
            - InputModel
            - OutputModel
            - PydanticPrompt
            - BoolIO
            - StringIO
            - PromptMixin

## 指标集合的提示

Ragas 中的现代指标使用专用提示类。每个指标模块包含：

- **输入模型**：定义提示所需的数据（如 `FaithfulnessInput`）
- **输出模型**：定义 LLM 响应的预期结构（如 `FaithfulnessOutput`）
- **提示类**：继承 `BasePrompt`，用于生成带示例与指令的提示字符串

### 示例：Faithfulness 指标提示

```python
from ragas.metrics.collections.faithfulness.util import (
    FaithfulnessPrompt,
    FaithfulnessInput,
    FaithfulnessOutput,
)

# 提示类将输入/输出模型与指令和示例结合
prompt = FaithfulnessPrompt()

# 创建输入数据
input_data = FaithfulnessInput(
    response="The capital of France is Paris.",
    context="Paris is the capital and most populous city of France."
)

# 为 LLM 生成提示字符串
prompt_string = prompt.to_string(input_data)

# 输出将按 FaithfulnessOutput 模型的结构组织
```

### 可用指标提示

各指标提示的详细说明请参见对应指标文档：

- [Faithfulness](../concepts/metrics/available_metrics/faithfulness.md)
- [Context Recall](../concepts/metrics/available_metrics/context_recall.md)
- [Context Precision](../concepts/metrics/available_metrics/context_precision.md)
- [Answer Correctness](../concepts/metrics/available_metrics/answer_correctness.md)
- [Factual Correctness](../concepts/metrics/available_metrics/factual_correctness.md)
- [Noise Sensitivity](../concepts/metrics/available_metrics/noise_sensitivity.md)

## 自定义

关于在指标中自定义提示的详细说明，请参阅 [在指标中修改提示](../howtos/customizations/metrics/modifying-prompts-metrics.md)。
