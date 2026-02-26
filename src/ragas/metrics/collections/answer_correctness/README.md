# Answer Correctness（答案正确性）

## 功能概述

通过**多步流水线**评估答案正确性，综合**事实性（Factuality）**与**语义相似度（Similarity）**。

## 核心逻辑

1. **陈述生成**：用 LLM 将「回答」与「参考答案」分别拆成原子陈述（Statement）
2. **分类**：用 LLM 对回答中的陈述做 TP/FP/FN 分类（相对参考答案）
3. **事实性分数**：由 TP/FP/FN 计算 F-β（默认 F1）
4. **相似度分数**：用 Embedding 计算回答与参考的余弦相似度（可选，权重可设为 0）
5. **最终分数**：`weights[0] * factuality + weights[1] * similarity`，默认 `[0.75, 0.25]`

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `AnswerCorrectness`：流水线编排、陈述生成、分类、F1 计算、相似度、加权合并 |
| `util.py` | 陈述生成 / 正确性分类的输入输出模型与 Prompt（含丰富示例） |

## 依赖

- **LLM**：陈述生成 + 正确性分类
- **Embeddings**（可选）：当 `weights[1] > 0` 时必选，用于语义相似度

## 关键参数

- `weights`: `[factuality_weight, similarity_weight]`，需至少一个非 0
- `beta`: F-β 的 β，>1 更重视 recall，<1 更重视 precision

## 使用示例

```python
metric = AnswerCorrectness(llm=llm, embeddings=embeddings, weights=[0.75, 0.25])
result = await metric.ascore(
    user_input="法国首都是哪？",
    response="巴黎是法国首都，且有很多博物馆。",
    reference="巴黎是法国首都。",
)
```
