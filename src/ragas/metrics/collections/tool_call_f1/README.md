# Tool Call F1（工具调用 F1）

## 功能概述

**无 LLM** 的规则指标：将预测的工具调用与参考工具调用视为**集合**，按「名称 + 参数」完全一致判定 TP/FP/FN，计算 F1。

## 核心逻辑

1. 从 `user_input` 中收集所有 `AIMessage` 的 `tool_calls` 作为预测集
2. 将 `reference_tool_calls` 作为参考集
3. 工具调用转为可哈希形式（name + 参数集合），用集合运算求 TP、FP、FN
4. F1 = 2 * P * R / (P + R)，无 TP 且无 FP/FN 时按实现返回 0 或 1

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ToolCallF1`：从消息中抽取预测、转为集合、计算 F1 |
| `util.py` | `tool_call_to_hashable`、`calculate_f1_score` 等工具函数 |

## 依赖

- 无 LLM/Embedding，仅依赖 `ragas.messages` 中的消息与 ToolCall 结构

## 使用示例

```python
metric = ToolCallF1()
result = await metric.ascore(
    user_input=[HumanMessage(...), AIMessage(..., tool_calls=[...])],
    reference_tool_calls=[ToolCall(name="get_weather", args={"location": "Paris"})],
)
```
