# Context Relevance（上下文相关性）

## 功能概述

评估**检索到的上下文**与**用户问题**的相关性，采用**双评委**取平均，提高稳定性。

## 核心逻辑

1. 将 `retrieved_contexts` 拼接成一段 context
2. **Judge 1 / Judge 2**：分别对「问题 + context」打分，刻度 0/1/2（不相关 / 部分相关 / 完全相关）
3. 最终分数 = (judge1/2 + judge2/2) / 2，归一化到 0.0–1.0
4. 边界情况：问题或 context 为空、问题与 context 完全相同等，直接返回 0

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ContextRelevance`：双评委调用、边界处理、取平均、重试 |
| `util.py` | 两个评委的输入/输出模型与 Prompt 示例 |

## 依赖

- **LLM**：双评委打分

## 使用示例

```python
metric = ContextRelevance(llm=llm)
result = await metric.ascore(
    user_input="爱因斯坦何时出生？",
    retrieved_contexts=["阿尔伯特·爱因斯坦出生于 1879 年 3 月 14 日。"],
)
```
