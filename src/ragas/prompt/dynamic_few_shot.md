# dynamic_few_shot.py 功能说明

## 概述

`dynamic_few_shot.py` 提供 **动态少样本提示词**：在每次 `format()` 时，根据当前输入与示例库中条目的 **相似度** 动态选取 top-k 条示例加入 prompt，而不是使用固定示例列表。包含 **SimpleExampleStore** 抽象、**SimpleInMemoryExampleStore** 实现，以及继承 **Prompt** 的 **DynamicFewShotPrompt**。

## 主要组件

### 1. SimpleExampleStore（抽象基类）

- **get_examples(data, top_k)**：根据输入 `data`（dict）返回最相关的 top_k 条示例，每条为 `(input_dict, output_dict)`。
- **add_example(input_dict, output_dict)**：向库中添加一条示例。

### 2. SimpleInMemoryExampleStore

- **存储**：`_examples` 为 (input, output) 列表；若有 `embedding_model`，则 `_embeddings_list` 存每条 input 的嵌入向量。
- **_get_embedding(data)**：将 data 转为字符串（如 "k: v" 行）后调用 `embedding_model.embed_query`。
- **add_example**：追加 (input, output)，若有 embedding_model 则计算 input 的 embedding 并追加到 _embeddings_list。
- **get_examples(data, top_k, threshold)**：
  - 无示例或未配置 embedding：返回最近 top_k 条（按加入顺序）；
  - 否则：对 data 算 query embedding，调用 _get_nearest_examples（余弦相似度 ≥ threshold 的条目的 top_k 下标），再按下标从 _examples 取回。
- **_get_nearest_examples**：numpy 算余弦相似度，过滤 ≥ threshold，按相似度排序取 top_k 下标；若无满足条件的则退回“最近 top_k 条”。

### 3. DynamicFewShotPrompt(Prompt)

- **构造**：接收 instruction、examples（可选）、response_model、embedding_model、max_similar_examples、similarity_threshold；内部创建 SimpleInMemoryExampleStore，父类用空 examples 初始化，再把传入的 examples 逐个 add 到 store。
- **format(**kwargs)**：用 kwargs 填充 instruction；若 kwargs 非空且存在 example_store，则从 store 取 `max_similar_examples` 条（阈值 `similarity_threshold`），格式化为 “Examples: …” 拼到 instruction 后。
- **add_example**：若 (input, output) 不在 store._examples 中则加入 store（不重复）。
- **from_prompt(cls, prompt, embedding_model, ...)**：从已有 Prompt 实例创建 DynamicFewShotPrompt，拷贝 instruction、examples、response_model 并配置 embedding 与 top_k/阈值。
- **save(path, include_embeddings=True)**：存 JSON（或 .gz），含 type="DynamicFewShotPrompt"、instruction、examples、max_similar_examples、similarity_threshold、response_model_info、embedding_model_info；可选写入 embeddings 列表。
- **load(path, response_model=None, embedding_model=None)**：校验 type、必要时要求 response_model/embedding_model；恢复配置与 examples，若有保存的 embeddings 且长度匹配则写回 example_store._embeddings_list。

## 使用场景

- 示例很多，但希望每次只放与当前输入最相关的几条，减少 token 并提升相关性。
- 与简单 Prompt 兼容：可从现有 Prompt 用 `from_prompt` 转成 DynamicFewShotPrompt，只需提供 embedding_model。
