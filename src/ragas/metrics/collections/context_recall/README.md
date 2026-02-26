# Context Recall（上下文召回率）

## 功能概述

评估**检索到的上下文**是否覆盖了**参考答案中的信息**。将参考答案拆成陈述，逐条判断「是否可由检索上下文支撑」，召回率 = 可支撑陈述数 / 总陈述数。

## 核心逻辑

1. 将 `retrieved_contexts` 合并成一段 context 文本
2. 用 LLM 对「参考答案」中的每条陈述做**归因（attribution）**：能否从 context 中推断出该陈述
3. 输出为带 `attributed`（0/1）的分类列表
4. 分数 = sum(attributed) / len(classifications)

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ContextRecall`：组 context、调用 LLM、汇总 attributed 比例 |
| `util.py` | 输入（question, context, answer）、输出（每条陈述的 attributed + reason）及 Prompt 示例 |

## 依赖

- **LLM**：对答案中的陈述做「是否可由 context 归因」的分类

## 使用示例

```python
metric = ContextRecall(llm=llm)
result = await metric.ascore(
    user_input="法国首都是哪？",
    retrieved_contexts=["巴黎是法国首都。"],
    reference="巴黎是法国首都和最大城市。",
)
```
