# Instance Specific Rubrics（样本级 rubric）

## 功能概述

与 Domain Specific Rubrics 类似，但 **rubric 由每个样本自己提供**：每次调用 `ascore` 时传入该条样本的 `rubrics` 字典，适用于不同题目需要不同评分标准的情况。

## 核心逻辑

1. 必须传入 `rubrics`（如 score1_description … score5_description）
2. 与 user_input、response、retrieved_contexts、reference 等一起组成 InstanceRubricScoreInput
3. LLM 按该条样本的 rubric 输出 score 与 feedback；`allowed_values=(1.0, 5.0)`

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `InstanceSpecificRubrics`：校验 rubrics、组 input、调 LLM |
| `util.py` | `InstanceRubricScoreInput/Output` 与 `InstanceRubricScorePrompt` |

## 依赖

- **LLM**：按实例 rubric 打分

## 使用示例

```python
metric = InstanceSpecificRubrics(llm=llm)
rubrics = {
    "score1_description": "完全偏题",
    "score5_description": "全面且准确",
    # ...
}
result = await metric.ascore(
    user_input="解释量子计算",
    response="量子计算使用量子比特……",
    rubrics=rubrics,
)
```
