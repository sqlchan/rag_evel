# Context Precision（上下文精确度）

## 功能概述

评估**检索到的上下文**对「回答问题」是否有用。对每个检索片段做二元判定（有用/无用），再按顺序计算**平均精度（Average Precision）**。

## 两种指标

### ContextPrecisionWithReference

- 以**参考答案**为「正确回答」，判断每个 context 是否有助于得到该答案
- 输入：`user_input`, `reference`, `retrieved_contexts`

### ContextPrecisionWithoutReference

- 以**模型生成的回答**为「答案」，判断每个 context 是否有助于该回答
- 输入：`user_input`, `response`, `retrieved_contexts`

## 核心逻辑

1. 对每个 `retrieved_contexts` 中的条目，用 LLM 给出 verdict（0 或 1）
2. 按顺序计算 AP：对每个「有用」位置，累加「到该位置为止的精度」再除以「有用」总数

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ContextPrecisionWithReference` / `ContextPrecisionWithoutReference`，以及别名 `ContextPrecision`、`ContextUtilization` |
| `util.py` | 单条 context 评估的输入/输出模型与 Prompt 示例 |

## 依赖

- **LLM**：判断「context 是否有助于得到给定 answer」

## 使用示例

```python
metric = ContextPrecisionWithReference(llm=llm)
result = await metric.ascore(
    user_input="法国首都是哪？",
    reference="巴黎是法国首都。",
    retrieved_contexts=["巴黎是法国首都和最大城市。", "柏林是德国首都。"],
)
```
