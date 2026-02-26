# mixin.py 功能说明

## 概述

`PromptMixin` 是一个 **Mixin 类**，为宿主类提供“**管理一组 PydanticPrompt**”的能力：发现、按名称获取/设置、保存到目录、从目录加载、以及用 LLM 适配到目标语言。常用于 Synthesizer、MetricWithLLM 等需要多个结构化 prompt 的类。

## 主要接口

### 1. _get_prompts() -> Dict[str, PydanticPrompt]

- 通过 `inspect.getmembers(self)` 找出所有 **属性值为 PydanticPrompt 的成员**，返回 `{属性名: prompt}`。
- 内部使用，键为“类上的变量名”。

### 2. get_prompts() -> Dict[str, PydanticPrompt]

- 返回 `{prompt.name: prompt}`，即按 **prompt 的 name** 索引的字典。
- 对外推荐用此接口按“业务名称”取 prompt。

### 3. set_prompts(**prompts)

- 按 **prompt 名称**（name）设置 prompt。
- 仅接受当前类已有的 prompt 名称，且值必须为 `PydanticPrompt` 实例，否则抛出 `ValueError`。
- 内部通过 `name_to_var` 找到对应属性名并 `setattr`。

### 4. adapt_prompts(language, llm, adapt_instruction=False) -> Dict[str, PydanticPrompt]

- 对 `get_prompts()` 中每个 prompt 调用其 `adapt(language, llm, adapt_instruction)`，返回适配后的 `{name: adapted_prompt}`。
- 若需持久化，应再调用 `save_prompts()`；加载时用 `load_prompts()`。

### 5. save_prompts(path)

- `path` 必须为已存在的目录。
- 对每个 prompt 写入一个 JSON 文件，命名规则：
  - 若 `self.name == ""`：`{prompt_name}_{language}.json`
  - 否则：`{self.name}_{prompt_name}_{language}.json`
- 实际写入由各 prompt 的 `save()` 完成。

### 6. load_prompts(path, language=None)

- 从目录加载 prompt；`language` 默认 `"english"`。
- 文件名与 `save_prompts` 对应；通过 `prompt.__class__.load(file_name)` 加载并得到 `{prompt_name: loaded_prompt}`。
- 注意：只加载，不自动 `set_prompts()`，调用方可按需把返回的 dict 再 set 回对象。

## 使用场景

- **BaseSynthesizer / MetricWithLLM**：类上定义多个 `PydanticPrompt` 属性，通过 Mixin 统一管理、保存、加载、多语言适配。
- 用户可通过 `get_prompts()` 查看名称，用 `set_prompts(name=custom_prompt)` 替换为自定义 prompt。
