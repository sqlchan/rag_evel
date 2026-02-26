# Answer Relevancy（答案相关性）

## 功能概述

评估**回答是否切题**：从回答反推「可回答的问题」，再与原始问题做语义比较；并识别敷衍/回避型回答（noncommittal）。

## 核心逻辑

1. **生成问题**：用 LLM 根据回答生成若干「可由该回答回答的问题」（次数由 `strictness` 控制，默认 3）
2. **Noncommittal 标记**：每次生成同时输出该回答是否敷衍/含糊（如「不知道」「看情况」）
3. **语义比较**：用 Embedding 对「原始问题」与「生成的问题」做向量化，计算余弦相似度
4. **最终分数**：生成问题的平均相似度；若全部被标为 noncommittal，则分数为 0

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `AnswerRelevancy`：多轮问题生成、embed、相似度、noncommittal 处理 |
| `util.py` | 问题生成与 noncommittal 的输入/输出模型及 Prompt 示例 |

## 依赖

- **LLM**：生成「可由回答推导出的问题」及 noncommittal 标签
- **Embeddings**：原始问题与生成问题的向量化与相似度

## 关键参数

- `strictness`：生成问题的个数，越大评估越严格

## 使用示例

```python
metric = AnswerRelevancy(llm=llm, embeddings=embeddings, strictness=3)
result = await metric.ascore(
    user_input="法国首都是哪？",
    response="巴黎是法国首都。",
)
```
