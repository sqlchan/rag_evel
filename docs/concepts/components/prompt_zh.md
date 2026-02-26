# 提示对象

Ragas 中的提示用于各类指标与合成数据生成任务。在这些任务中，Ragas 也支持用户修改或替换默认提示为自定义提示。本指南概述 Ragas 中的提示对象。

## 提示对象的组成

在 Ragas 中，提示对象由以下关键部分组成：

1. **指令（Instruction）**：任何提示的基础元素，是用自然语言清晰描述语言模型（LLM）应执行任务的指示，通过提示对象中的 `instruction` 变量指定。

2. **少样本示例（Few-Shot Examples）**：提供少样本示例时 LLM 通常表现更好，有助于模型理解任务上下文并生成更准确的回答。这些示例通过提示对象的 `examples` 变量指定。每个示例包含输入及其对应输出，供 LLM 学习任务。

3. **输入模型（Input Model）**：每个提示都期望有输入以产生输出。在 Ragas 中，该输入的期望格式由 `input_model` 变量定义。这是一个 Pydantic 模型，描述输入结构，支持对传入提示的数据进行校验与解析。

4. **输出模型（Output Model）**：执行后提示会生成输出。该输出的格式由提示对象中的 `output_model` 变量指定。与输入模型类似，输出模型也是 Pydantic 模型，定义输出结构，便于对 LLM 产生数据进行校验与解析。

## 示例

以下是一个为文本生成任务定义提示的提示对象示例：

```python
from ragas.prompt import PydanticPrompt
from pydantic import BaseModel, Field

class MyInput(BaseModel):
    question: str = Field(description="要回答的问题")

class MyOutput(BaseModel):
    answer: str = Field(description="问题的答案")

class MyPrompt(PydanticPrompt[MyInput,MyInput]):
    instruction = "回答给定的问题"
    input_model = MyInput
    output_model = MyOutput
    examples = [
        (
            MyInput(question="谁在构建 LLM 应用评估的开源标准？"),
            MyOutput(answer="Ragas")
        )
    ]
    
```

## 编写有效提示的指南

在 Ragas 中创建提示时，可参考以下指南以确保提示有效且符合任务要求：

1. **指令清晰简洁**：用清晰、简洁的指令明确 LLM 应执行的任务。指令含糊可能导致回答不准确。
2. **少样本示例相关**：包含与任务相关的少样本示例，覆盖多样化场景（建议 3–5 个）。这些示例帮助 LLM 理解上下文并生成准确回答。
3. **输入与输出模型简单直观**：定义简单、直观的输入和输出模型，准确表示 LLM 期望的数据格式和 LLM 生成的输出格式。若模型较复杂，可尝试将任务拆成更小的子任务，并为各子任务使用独立提示。
