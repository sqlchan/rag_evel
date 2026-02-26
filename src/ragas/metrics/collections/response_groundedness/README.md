# Response Groundedness（回答 grounded 程度）

## 功能概述

评估**回答是否基于给定上下文**，即回答中的主张是否被 retrieved_contexts 支持。采用**双评委**，刻度 0/1/2，取平均后归一化到 0.0–1.0。

## 核心逻辑

1. 将 `retrieved_contexts` 合并为一段 context
2. **Judge 1 / Judge 2**：对「response + context」打分（0=无支撑，1=部分支撑，2=完全支撑）
3. 最终分数 = (judge1/2 + judge2/2) / 2；空 response 或空 context 时返回 0

## 与 Faithfulness 的区别

- **Faithfulness**：先把回答拆成陈述，再逐条用 NLI 判是否被 context 支持
- **Response Groundedness**：整体对「回答 + 上下文」做双评委打分，更偏整体观感

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ResponseGroundedness`：双评委、取平均、重试与 NaN 处理 |
| `util.py` | 两个评委的输入/输出模型与 Prompt 示例 |

## 依赖

- **LLM**：双评委

## 使用示例

```python
metric = ResponseGroundedness(llm=llm)
result = await metric.ascore(
    response="爱因斯坦 1879 年生于德国。",
    retrieved_contexts=["阿尔伯特·爱因斯坦 1879 年 3 月 14 日生于德国乌尔姆。"],
)
```
