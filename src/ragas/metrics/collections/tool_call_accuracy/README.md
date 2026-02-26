# Tool Call Accuracy（工具调用准确度）

## 功能概述

**规则指标**：比较预测的工具调用序列与参考序列的**顺序**和**参数**。支持严格顺序（strict_order=True）或忽略顺序（False）。

## 核心逻辑

1. 从 `user_input` 中按顺序收集所有 `AIMessage` 的 `tool_calls`
2. 若 `strict_order=False`，对预测与参考按名称等排序后再对齐
3. **序列对齐**：严格模式要求名称序列完全一致；非严格模式要求排序后一致
4. **参数准确度**：对对齐后的每对 tool call，用 `exact_match_args` 比较参数（递归比较字典/列表等）
5. 最终分数 = (平均参数得分) × 序列对齐系数 × 长度覆盖惩罚（若预测与参考长度不一致）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ToolCallAccuracy`：序列抽取、对齐判断、参数比较、覆盖惩罚 |
| `util.py` | `exact_match_args`、`sorted_key_for_tool_call` 等 |

## 依赖

- 无 LLM，仅依赖消息与 ToolCall 结构

## 使用示例

```python
metric = ToolCallAccuracy(strict_order=True)
result = await metric.ascore(
    user_input=[..., AIMessage(..., tool_calls=[...])],
    reference_tool_calls=[...],
)
```
