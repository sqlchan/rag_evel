# Multi Modal Faithfulness（多模态忠实度）

## 功能概述

评估**回答是否忠实于多模态检索上下文**（文本 + 图像）。context 可以是文本字符串或图片路径/URL/base64；需要**带视觉能力的 LLM**（如 gpt-4o、claude-3-opus）。

## 核心逻辑

1. 用 `build_multimodal_message_content` 将 instruction、response、retrieved_contexts 组装成多模态消息（文本块 + 图片块）
2. 调用 LLM 的 vision API（根据 provider 选 Google 或 OpenAI 等），返回 structured output：faithful（bool）与 reason
3. 分数：faithful 为 1.0，否则 0.0

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `MultiModalFaithfulness`：校验输入、构建多模态 content、调 vision API、映射分数 |
| `util.py` | `MULTIMODAL_FAITHFULNESS_INSTRUCTION`、`build_multimodal_message_content`、输出模型 |

## 依赖

- **LLM**：需支持 vision（InstructorLLM），如 gpt-4o

## 使用示例

```python
metric = MultiModalFaithfulness(llm=llm)
result = await metric.ascore(
    response="图中是特斯拉 Model X，一款电动 SUV。",
    retrieved_contexts=["path/to/tesla_image.jpg", "特斯拉生产电动车。"],
)
```
