# Context Entity Recall（上下文实体召回）

## 功能概述

基于**实体**的召回率：从参考答案与检索上下文中抽取实体，计算**参考实体中有多少出现在上下文中**。

公式：`Context Entity Recall = |CN ∩ GN| / |GN|`  
- CN = 上下文中出现的实体集合  
- GN = 参考答案（ground truth）中的实体集合  

## 核心逻辑

1. 用 LLM 从 `reference` 中抽取实体列表
2. 用 LLM 从合并后的 `retrieved_contexts` 中抽取实体列表
3. 取两个集合的交集，recall = |交集| / |参考实体集|（空参考时加小常数防除零）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `ContextEntityRecall`：分别对 reference 与 context 抽实体、算召回 |
| `util.py` | 实体抽取的输入/输出模型与 Prompt（实体含人名、地点、组织、日期等） |

## 依赖

- **LLM**：实体抽取（结构化输出为 entities 列表）

## 使用示例

```python
metric = ContextEntityRecall(llm=llm)
result = await metric.ascore(
    reference="巴黎是法国首都，建立于公元前 52 年。",
    retrieved_contexts=["法国首都是巴黎。", "该城建于古代。"],
)
```
