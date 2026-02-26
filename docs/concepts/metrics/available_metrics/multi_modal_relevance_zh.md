## 多模态相关性

`MultiModalRelevance` 衡量生成答案与**视觉和文本**上下文的相关性。由用户输入、回答与检索上下文（视觉与文本）计算，分数缩放到 (0,1)，越高表示越相关。

若回答与提供的视觉或文本上下文一致，则视为相关。判断时直接将回答与给定上下文对比，相关性分数为 0 或 1。

### 示例（推荐：Collections API）

（代码与原文一致，见 [multi_modal_relevance.md](multi_modal_relevance.md)。）

### 支持的上下文类型

- 文本上下文、图片 URL、本地图片路径、Base64 数据 URI（同多模态忠实度）。

### 要求

- 需要支持视觉的 LLM；使用 Collections API 时用 `llm_factory` 创建 LLM 实例。

### 旧版 API

!!! warning "已弃用"
    旧版 API 已弃用，将在后续版本移除。请迁移到上文所示的 Collections API。
