# utils.py 功能说明

## 概述

`utils.py` 提供与 **Prompt 无关** 的通用工具函数，主要用于：在嵌套结构（含 Pydantic 模型）中 **收集/替换字符串**，以及从 LLM 输出中 **提取 JSON 片段**。被 `pydantic_prompt`、`metrics/base_prompt` 等模块使用。

## 函数说明

### 1. get_all_strings(obj) -> list[str]

- **作用**：从任意嵌套结构中递归收集所有字符串。
- **支持类型**：
  - `str` → 直接加入列表；
  - `BaseModel` → 对 `model_dump()` 的每个字段值递归；
  - `list` / `tuple` → 对每个元素递归；
  - `dict` → 对每个 value 递归。
- **用途**：多语言适配时，先收集 prompt 中所有待翻译字符串，再批量翻译后用 `update_strings` 填回。

### 2. update_strings(obj, old_strings, new_strings) -> Any

- **作用**：在相同结构的对象中，将 `old_strings` 中出现的字符串按位置替换为 `new_strings` 中的对应项。
- **约束**：`len(old_strings) == len(new_strings)`，否则抛出 `ValueError`。
- **逻辑**：对 `str` 做逐项替换；对 `BaseModel` 深拷贝后按字段递归替换；对 list/tuple/dict 递归替换其元素/值；其他类型深拷贝返回。
- **用途**：翻译完成后，用“原句列表”和“译句列表”更新 examples 等嵌套结构，保持结构不变。

### 3. extract_json(text) -> str

- **作用**：从一段文本中 **提取第一个完整的 JSON 结构**（以 `[` 或 `{` 开始，到匹配的 `]` 或 `}` 结束）。
- **逻辑**：
  - 若存在 ` ```json `，则从该位置开始查找；
  - 否则在全文找第一个 `[` 或 `{`，确定配对的 `]` 或 `}`（用计数器匹配括号）；
  - 返回该子串；若无合法括号或未闭合则返回原文本。
- **用途**：LLM 返回可能带前后说明或 markdown，用此函数取出纯 JSON 再交给 Pydantic 解析。
