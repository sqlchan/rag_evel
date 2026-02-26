import copy
import typing as t

from pydantic import BaseModel


def get_all_strings(obj: t.Any) -> list[str]:
    """
    Get all strings in the objects.
    递归收集嵌套结构（含 Pydantic 模型、list、dict）中的全部字符串，用于多语言翻译前提取待翻译文本。
    """
    strings = []

    if isinstance(obj, str):
        strings.append(obj)
    elif isinstance(obj, BaseModel):
        # Pydantic 模型：遍历 model_dump() 的每个字段值递归收集
        for field_value in obj.model_dump().values():
            strings.extend(get_all_strings(field_value))
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            strings.extend(get_all_strings(item))
    elif isinstance(obj, dict):
        for value in obj.values():
            strings.extend(get_all_strings(value))

    return strings


def update_strings(obj: t.Any, old_strings: list[str], new_strings: list[str]) -> t.Any:
    """
    Replace strings in the object with new strings.
    Example Usage:
    ```
    old_strings = ["old1", "old2", "old3"]
    new_strings = ["new1", "new2", "new3"]
    obj = {"a": "old1", "b": "old2", "c": ["old1", "old2", "old3"], "d": {"e": "old2"}}
    update_strings(obj, old_strings, new_strings)
    ```
    """
    if len(old_strings) != len(new_strings):
        raise ValueError("The number of old and new strings must be the same")

    # 按位置一对一替换：old_strings[i] -> new_strings[i]
    def replace_string(s: str) -> str:
        for old, new in zip(old_strings, new_strings):
            if s == old:
                return new
        return s

    if isinstance(obj, str):
        return replace_string(obj)
    elif isinstance(obj, BaseModel):
        new_obj = copy.deepcopy(obj)
        for field in new_obj.__class__.model_fields:
            setattr(
                new_obj,
                field,
                update_strings(getattr(new_obj, field), old_strings, new_strings),
            )
        return new_obj
    elif isinstance(obj, list):
        return [update_strings(item, old_strings, new_strings) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(update_strings(item, old_strings, new_strings) for item in obj)
    elif isinstance(obj, dict):
        return {k: update_strings(v, old_strings, new_strings) for k, v in obj.items()}

    return copy.deepcopy(obj)


def extract_json(text: str) -> str:
    """Identify json from a text blob by matching '[]' or '{}'.

    Warning: This will identify the first json structure!"""

    # 若存在 ```json 代码块标记，则从该位置开始查找，避免把说明文字当 JSON
    md_json_idx = text.find("```json")
    if md_json_idx != -1:
        text = text[md_json_idx:]

    # 查找第一个 [ 或 {，以确定 JSON 的起始边界
    left_bracket_idx = text.find("[")
    left_brace_idx = text.find("{")

    indices = [idx for idx in (left_bracket_idx, left_brace_idx) if idx != -1]
    start_idx = min(indices) if indices else None

    # If no delimiter found, return the original text
    if start_idx is None:
        return text

    # Identify the exterior delimiters defining JSON
    open_char = text[start_idx]
    close_char = "]" if open_char == "[" else "}"

    # 用括号计数匹配：遇到开始符 +1，结束符 -1，归零时得到完整 JSON 子串
    count = 0
    for i, char in enumerate(text[start_idx:], start=start_idx):
        if char == open_char:
            count += 1
        elif char == close_char:
            count -= 1

        # 计数归零表示首尾括号配对，已包含完整一层 [] 或 {}
        if count == 0:
            return text[start_idx : i + 1]

    return text  # In case of unbalanced JSON, return the original text
