# Ragas Prompt 模块总览

本目录提供 Ragas 评估工具中与 **Prompt（提示词）** 相关的抽象与实现，用于与 LLM 交互、结构化输入输出、多模态与多语言支持等。

## 目录结构

```
prompt/
├── __init__.py          # 模块导出
├── base.py               # 抽象基类 BasePrompt、StringPrompt、IO 模型
├── utils.py              # 字符串提取/替换、JSON 解析等工具
├── mixin.py              # PromptMixin：为类提供 prompt 的获取/设置/保存/加载/适配
├── simple_prompt.py      # Prompt：简单提示词（占位符 + 少样本 + 可选 response_model）
├── pydantic_prompt.py    # PydanticPrompt：基于 Pydantic 输入/输出模型的提示词
├── dynamic_few_shot.py   # 动态少样本提示词（按相似度选取示例）
├── few_shot_pydantic_prompt.py  # 少样本版 PydanticPrompt（示例库 + 相似度检索）
├── multi_modal_prompt.py # 图文多模态提示词（ImageTextPrompt / ImageTextPromptValue）
└── metrics/              # 各评估指标专用的 prompt 函数与基类
```

## 核心概念

| 类型 | 说明 |
|------|------|
| **BasePrompt** | 抽象基类：定义 `generate` / `generate_multiple`、`save` / `load`，以及 name、language 等属性。 |
| **StringPrompt** | 纯字符串提示词：直接将传入的字符串作为 prompt 调用 LLM，无模板与结构化输出。 |
| **PydanticPrompt** | 输入/输出均为 Pydantic 模型：instruction + 输出 JSON Schema + 示例 + 当前输入，支持解析、重试、多语言适配。 |
| **Prompt (simple_prompt)** | 简单提示词：instruction 模板（如 `{question}`）+ 可选的少样本列表 + 可选 response_model，侧重 `format()` 与 JSON 序列化保存。 |
| **DynamicFewShotPrompt** | 继承 Prompt：示例存入“示例库”，format 时按与当前输入的相似度动态选取 top-k 示例。 |
| **FewShotPydanticPrompt** | 继承 PydanticPrompt：示例存在 ExampleStore，每次 generate 时按相似度从库中取示例再调用父类生成。 |
| **ImageTextPrompt** | 多模态：输入可包含文本与图片（URL/Base64/本地路径），生成 ImageTextPromptValue 供多模态 LLM 使用。 |
| **PromptMixin** | Mixin：为任意类提供 `get_prompts()`、`set_prompts()`、`save_prompts()`、`load_prompts()`、`adapt_prompts()`。 |

## 使用关系

- **评估流程**：各 Metric 通常通过 `PromptMixin` 持有多个 `PydanticPrompt`，或直接使用 `metrics/` 下的函数式 prompt。
- **多语言**：`PydanticPrompt.adapt()` 与 `BasePrompt.adapt()`（metrics）将示例与可选 instruction 翻译为目标语言；Mixin 的 `adapt_prompts()` 对类内所有 prompt 统一适配。
- **持久化**：`BasePrompt.save/load` 存 JSON（含 ragas_version、language、instruction、examples 等）；Simple Prompt / DynamicFewShotPrompt 另有 format_version、type、可选 .gz 压缩。

## 相关文档

- 各子模块功能详见同目录下的 `base.md`、`utils.md`、`simple_prompt.md`、`pydantic_prompt.md`、`dynamic_few_shot.md`、`few_shot_pydantic_prompt.md`、`multi_modal_prompt.md`、`mixin.md`。
- 指标相关 prompt 见 `metrics/README.md` 及各 `metrics/*.md`。
