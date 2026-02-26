# Agent Goal Accuracy（智能体目标准确度）

## 功能概述

评估**智能体工作流**是否达成用户目标，支持「有参考答案」与「无参考答案」两种模式。

## 两种指标

### AgentGoalAccuracyWithReference

- **输入**：对话消息列表 + **参考结果**（期望达成的结果描述）
- **流程**：从对话推断「最终状态」→ 与参考结果比较 → 输出 0/1

### AgentGoalAccuracyWithoutReference

- **输入**：仅对话消息列表
- **流程**：从对话推断「用户目标」和「最终状态」→ 比较二者是否一致 → 输出 0/1

## 核心逻辑

1. **格式化对话**：将 `HumanMessage` / `AIMessage` / `ToolMessage` 转为可读文本
2. **推断结果**：用 `InferGoalOutcomePrompt` 得到 `user_goal` 与 `end_state`
3. **比较**：用 `CompareOutcomePrompt` 判断「期望结果」与「实际结果」是否一致，得到 verdict 0 或 1

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `AgentGoalAccuracyWithReference` / `AgentGoalAccuracyWithoutReference`，以及别名 `AgentGoalAccuracy` |
| `util.py` | 工作流输入、目标/状态输出、比较输入输出的模型与两个 Prompt |

## 依赖

- **LLM**：推断目标/状态、比较结果

## 使用示例

```python
# 有参考
metric = AgentGoalAccuracyWithReference(llm=llm)
result = await metric.ascore(
    user_input=[HumanMessage(...), AIMessage(...), ToolMessage(...)],
    reference="在中餐馆订到晚上 8 点的桌",
)

# 无参考
metric = AgentGoalAccuracyWithoutReference(llm=llm)
result = await metric.ascore(user_input=[...])
```
