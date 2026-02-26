# Answer Accuracy（答案准确度）

## 功能概述

基于**双评委（Dual-Judge）**的答案准确度评估指标。将用户答案与参考答案对比，使用两个独立的评委提示取平均分，提高评估稳定性。

## 核心逻辑

1. **Judge 1**：直接比较「用户答案 vs 参考答案」
2. **Judge 2**：交换视角（用户答案与参考答案顺序对调）再评分，保证公平
3. **最终分数**：两评委分数取平均，并将 0/2/4 刻度归一化到 0.0–1.0

## 评分刻度

- **0**：不匹配（答案不在参考中或明显错误）
- **2**：部分匹配（部分正确）
- **4**：完全匹配（在术语、数字、日期、单位等各方面等价）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `AnswerAccuracy` 类：双评委调用、输入校验、取平均、重试逻辑 |
| `util.py` | Pydantic 输入/输出模型与两个评委的 Prompt 定义及示例 |

## 依赖

- **LLM**：需 `InstructorBaseRagasLLM`，用于执行两个评委的评分

## 使用示例

```python
metric = AnswerAccuracy(llm=llm)
result = await metric.ascore(
    user_input="爱因斯坦何时出生？",
    response="爱因斯坦于 1879 年出生。",
    reference="阿尔伯特·爱因斯坦于 1879 年 3 月 14 日出生。",
)
# result.value 在 0.0–1.0
```
