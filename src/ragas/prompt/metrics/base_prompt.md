# metrics/base_prompt.py 功能说明

## 概述

为 **指标** 提供的结构化 Prompt 基类：输入/输出为 Pydantic 模型，支持 **to_string**、**示例生成** 以及基于 Instructor LLM 的 **多语言 adapt**（翻译示例与可选 instruction）。与主目录的 `PydanticPrompt` 分离，便于指标只依赖轻量 BasePrompt 与函数式 prompt 混用。

## 主要组件

### BasePrompt[InputModel, OutputModel]

- **类属性**（子类需定义）：input_model、output_model、instruction、examples、language。
- **to_string(data)**：将 instruction + “请按如下 JSON Schema 输出” + output_model 的 schema + _generate_examples() + “当前 input” 拼成完整字符串。
- **_generate_examples()**：若 examples 非空，格式化为 "--------EXAMPLES-----------" + 多条 "Example i / Input: ... / Output: ..."；否则返回空串。
- **adapt(target_language, llm, adapt_instruction)**：用 get_all_strings 收集 examples 中所有字符串，调用 _translate_strings 批量翻译，再用 update_strings 写回；可选对 instruction 翻译；返回新 prompt 实例（language 更新为目标语言）。

### _translate_strings(strings, target_language, llm)

- 私有辅助：用固定翻译 instruction + json.dumps(strings) 构造 prompt，调用 **llm.agenerate(prompt, _TranslatedStrings)**，校验返回条数与输入一致后返回 statements 列表。
- _TranslatedStrings 为 Pydantic 模型，仅含 statements: List[str]。

## 与主目录 PydanticPrompt 的区别

- 不实现 generate/generate_multiple，不依赖 LangChain PromptValue、RagasOutputParser、fix_output_format 等；仅负责“拼 prompt 字符串”和“多语言适配”。
- 指标若需要直接调用 LLM，可自行用 to_string 得到字符串再调 LLM，或与 Instructor 等配合使用。
