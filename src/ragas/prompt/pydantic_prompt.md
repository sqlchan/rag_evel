# pydantic_prompt.py 功能说明

## 概述

`pydantic_prompt.py` 实现 **PydanticPrompt**：输入、输出均为 **Pydantic 模型** 的提示词类。支持 instruction、输出 JSON Schema、少样本 examples、与 LLM 的多种对接方式（Ragas LLM、Instructor、LangChain），以及 **输出解析失败时的自动重试**（通过 fix_output_format_prompt 让 LLM 修正格式）、**多语言适配**（翻译示例与可选 instruction）。

## 主要组件

### 1. PydanticPrompt[InputModel, OutputModel]

- **类属性**（子类需设置）：`input_model`、`output_model`、`instruction`、`examples`（(InputModel, OutputModel) 元组列表）。
- **to_string(data)**：将 instruction + 输出 Schema + 示例块 + “当前 input” 拼成完整 prompt 字符串。
- **process_input / process_output**：子类可重写，在生成前后对输入/输出做变换。
- **generate**：内部调 `generate_multiple(n=1)` 并返回第一个元素。
- **generate_multiple**：
  - 对 data 做 `process_input`，用 `to_string` 得到 prompt，创建 callback 组；
  - 根据 llm 类型分支：LangChain（agenerate_prompt 批处理）、Instructor（agenerate/generate + response_model）、BaseRagasLLM（generate）；
  - 对每条生成结果用 **RagasOutputParser** 解析为 OutputModel；若解析失败且 `retries_left > 0`，用 **fix_output_format_prompt** 让 LLM 修正输出再解析；
  - 对解析结果做 `process_output`，记录埋点后返回列表。
- **adapt(target_language, llm, adapt_instruction)**：用 `translate_statements_prompt` 翻译 examples 中所有字符串（及可选 instruction），返回新语言的新 prompt 实例。
- **save/load**：JSON 存/取 ragas_version、original_hash、language、instruction、examples（input/output 的 model_dump）；load 时用子类的 input_model/output_model 反序列化。

### 2. RagasOutputParser

- 继承 LangChain 的 `PydanticOutputParser`。
- **parse_output_string**：先用 `utils.extract_json` 从文本中提 JSON，再 `super().parse(jsonstr)`；若抛 `OutputParserException` 且 `retries_left > 0`，调用 **fix_output_format_prompt** 生成修正后的字符串再解析，否则抛出 **RagasOutputParserException**。

### 3. FixOutputFormat / fix_output_format_prompt

- 输入：`OutputStringAndPrompt`（output_string + prompt_value）；输出：`StringIO`。
- 用于“LLM 返回格式不符合 schema 时，再问一次 LLM 修正”。

### 4. TranslateStatements / translate_statements_prompt

- 输入：`ToTranslate`（target_language + statements 列表）；输出：`Translated`（statements 列表）。
- instruction 强调“只翻译、不执行指令、保持条数与顺序”；用于 **adapt()** 中批量翻译示例与可选 instruction。

### 5. is_langchain_llm(llm)

- 判断是否为 LangChain 的 BaseLanguageModel；若是会打 DeprecationWarning，建议改用 Ragas LLM 接口。

## 与其它模块关系

- **utils**：`get_all_strings`、`update_strings` 用于 adapt；`extract_json` 用于 RagasOutputParser。
- **mixin**：PromptMixin 收集类上的 PydanticPrompt，做 get/set/save/load/adapt。
- **few_shot_pydantic_prompt**：FewShotPydanticPrompt 继承 PydanticPrompt，在 generate_multiple 前从 ExampleStore 按相似度取 examples 再调 super。
- **multi_modal_prompt**：ImageTextPrompt 继承 PydanticPrompt，重写 to_prompt_value / _generate_examples / generate_multiple，支持图文输入。
