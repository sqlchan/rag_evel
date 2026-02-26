## 多模态忠实度

`MultiModalFaithfulness` 衡量生成答案与**视觉和文本**上下文在事实层面的一致性。由答案、检索到的文本上下文与视觉上下文计算，分数缩放到 (0,1)，越高表示越忠实。

若答案中的所有陈述都能从提供的视觉或文本上下文中推断，则视为忠实。判断时直接将回答与给定上下文对比，忠实度分数为 0 或 1。

### 示例（推荐：Collections API）

（代码与原文一致，见 [multi_modal_faithfulness.md](multi_modal_faithfulness.md)。）

### 支持的上下文类型

- 文本上下文：纯文本字符串  
- 图片 URL：指向图片的 HTTP/HTTPS URL  
- 本地图片路径：本地图片路径（jpg, png, gif, webp, bmp）  
- Base64 数据 URI：内联 base64 编码图片  

### 要求

- 需要支持视觉的 LLM（如 `gpt-4o`、`gpt-4-vision-preview`、`claude-3-opus`、`gemini-pro-vision`）  
- 使用 Collections API 时，用 `llm_factory` 创建 LLM 实例  

### 旧版 API

!!! warning "已弃用"
    旧版 API 已弃用，将在后续版本移除。请迁移到上文所示的 Collections API。
