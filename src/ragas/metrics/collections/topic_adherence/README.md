# Topic Adherence（主题遵循）

## 功能概述

评估**对话是否围绕给定主题**：系统是否只在「参考主题」内回答，并对超出主题的请求予以拒绝。支持 precision / recall / f1 三种聚合方式。

## 核心逻辑

1. **主题抽取**：从对话中抽取讨论到的主题列表
2. **是否回答**：对每个主题，用 LLM 判断模型是否「回答」了该主题（而非拒绝）
3. **是否在参考主题内**：用 LLM 判断每个主题是否属于 `reference_topics`
4. **计算**：TP=既回答又在参考内，FP=回答了但不在参考内，FN=在参考内但被拒绝；再按 mode 算 precision/recall/f1

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `TopicAdherence`：格式化对话、抽主题、回答判定、主题分类、TP/FP/FN 与 score |
| `util.py` | TopicExtraction、TopicRefused、TopicClassification 的输入/输出与 Prompt |

## 依赖

- **LLM**：主题抽取、是否拒绝、是否在参考主题内

## 使用示例

```python
metric = TopicAdherence(llm=llm, mode="precision")
result = await metric.ascore(
    user_input=[HumanMessage("讲讲量子物理"), AIMessage("量子物理是……")],
    reference_topics=["物理学", "科学"],
)
```
