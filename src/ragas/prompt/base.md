# base.py 功能说明

## 概述

`base.py` 定义 Ragas 中 **Prompt 的抽象基类** 以及最基础的 **字符串型 Prompt** 与 **简单 IO 模型**，供其它 prompt 实现与评估流水线使用。

## 主要组件

### 1. BasePrompt（抽象基类）

- **作用**：所有“可调用 LLM 的提示词”的抽象基类。
- **属性**：
  - `name`：未传入时用类名的 snake_case。
  - `language`：提示词语言，默认 `"english"`。
  - `original_hash`：可选，用于保存/加载时一致性校验。
- **抽象方法**：
  - `generate(llm, data, ...)`：单次生成，返回单条结果。
  - `generate_multiple(llm, data, n, ...)`：多次生成，返回列表。
- **实例方法**：
  - `save(file_path)`：将 ragas_version、language、original_hash 等写入 JSON；若文件已存在则报错。
  - `load(file_path)`：类方法，从 JSON 恢复 prompt，并做版本告警。

### 2. StringIO / BoolIO（Pydantic 模型）

- **StringIO**：仅含 `text: str`，用于“输出是一段字符串”的解析与哈希。
- **BoolIO**：仅含 `value: bool`，用于“输出是布尔”的解析与哈希。

### 3. StringPrompt（BasePrompt 子类）

- **作用**：最简单的 Prompt 实现——**不拼模板**，直接把传入的 `data`（str）当作完整 prompt 文本发给 LLM。
- **generate**：调用 `llm.agenerate_text(StringPromptValue(text=data), n=1, ...)`，返回第一条生成的 `text`。
- **generate_multiple**：同上但 `n=n`，返回 `[gen.text for gen in llm_result.generations[0]]`。
- **典型用法**：已有完整 prompt 字符串时，直接 `await prompt.generate(llm, data=full_prompt_str)`。

## 与其他模块的关系

- `PydanticPrompt`、`ImageTextPrompt` 等继承 `BasePrompt`，实现各自的 `generate` / `generate_multiple`。
- `mixin.PromptMixin` 通过 `inspect` 收集类上的 `PydanticPrompt` 实例，做统一 get/set/save/load/adapt。
- `base.save/load` 只存元数据；具体 instruction、examples 等由子类（如 `PydanticPrompt`）在各自 `save/load` 中序列化。
