# Multi Modal Relevance（多模态相关性）

## 功能概述

评估**回答是否与用户问题和多模态上下文相关**。上下文可包含文本与图像，需要**带视觉能力的 LLM**。

## 核心逻辑

1. 用 `build_multimodal_relevance_message_content` 将 instruction、user_input、response、retrieved_contexts 组装成多模态消息
2. 调用 LLM vision API，返回 structured output：relevant（bool）与 reason
3. 分数：relevant 为 1.0，否则 0.0

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `MultiModalRelevance`：输入校验、构建多模态 content、调 vision、映射分数 |
| `util.py` | `MULTIMODAL_RELEVANCE_INSTRUCTION`、`build_multimodal_relevance_message_content`、输出模型 |

## 依赖

- **LLM**：需支持 vision

## 使用示例

```python
metric = MultiModalRelevance(llm=llm)
result = await metric.ascore(
    user_input="图中是什么类型的车？",
    response="图中是特斯拉 Model X，一款电动 SUV。",
    retrieved_contexts=["path/to/tesla_image.jpg", "特斯拉生产电动车。"],
)
```
