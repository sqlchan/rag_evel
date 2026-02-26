# simple_prompt.py 功能说明

## 概述

`simple_prompt.py` 提供 **Prompt** 类：一种不依赖 Pydantic 输入/输出模型的“简单提示词”实现，支持 **instruction 模板（含占位符）**、**少样本示例列表**、可选的 **response_model**，以及 **JSON 序列化保存/加载**（含 .gz 压缩）。与 `pydantic_prompt` 相比，更轻量、偏“格式化 + 追踪使用情况”。

## 主要能力

### 1. 构造与属性

- **instruction**：str，可包含 `{placeholder}`，由 `format(**kwargs)` 填充。
- **examples**：`List[Tuple[Dict, Dict]]`，即 (input_dict, output_dict) 的少样本列表。
- **response_model**：可选 Pydantic 模型，仅用于“说明期望结构”，保存时只存 schema 信息，加载时需再次传入。

### 2. format(**kwargs) -> str

- 用 `kwargs` 填充 `instruction`，若有 `examples` 则追加“Examples: …”段落（每条为 Input/Output 的键值对展示）。
- 内部会触发一次 `PromptUsageEvent` 埋点（prompt_type="simple", has_examples, num_examples, has_response_model）。

### 3. 示例管理

- **add_example(input_dict, output_dict)**：要求均为 dict，追加到 `self.examples`。
- 初始化时也可传入 `examples` 列表，内部会逐个 `add_example`。

### 4. 持久化

- **save(path)**：
  - 写入 JSON（或 path 以 `.gz` 结尾时用 gzip）。
  - 内容：format_version、type="Prompt"、instruction、examples、response_model_info（若有）。
  - 若有 response_model 会警告“无法序列化，需在 load 时传入”。
- **load(path, response_model=None)**：
  - 校验 type 为 "Prompt"；若存了 response_model_info 但未传 response_model 则报错。
  - 恢复 instruction、examples、response_model；若提供了 response_model 且与保存的 schema 不一致会 warning。

### 5. 与 DynamicFewShotPrompt 的关系

- **DynamicFewShotPrompt** 继承 **Prompt**，将 examples 存到“示例库”（如 SimpleInMemoryExampleStore），`format()` 时按与当前输入的相似度动态选取示例，其余接口（如 save/load、response_model_info）在子类中有扩展（如 embedding、max_similar_examples 等）。

## 使用场景

- 快速搭一个带占位符和少量示例的 prompt，不需定义 Input/Output Pydantic 模型。
- 需要把 prompt 存成 JSON 便于版本管理或分享，且可接受“response_model 需手动传入”。
