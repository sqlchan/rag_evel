# few_shot_pydantic_prompt.py 功能说明

## 概述

`few_shot_pydantic_prompt.py` 提供基于 **Pydantic 输入/输出模型** 的 **少样本动态示例** 能力：示例存放在 **ExampleStore** 中，每次 **generate** 时根据当前输入的 **嵌入向量** 从库中按相似度取 top-k 条示例，再调用父类 **PydanticPrompt** 的 generate_multiple。与 `dynamic_few_shot` 的区别在于：这里输入/输出是 **BaseModel**，且与 **Ragas 的 PydanticPrompt 体系** 直接集成。

## 主要组件

### 1. ExampleStore（抽象基类）

- **get_examples(data: BaseModel, top_k, threshold)**：返回与 data 最相关的若干条示例，每条为 `(InputModel, OutputModel)`。
- **add_example(input: BaseModel, output: BaseModel)**：添加一条示例。

### 2. InMemoryExampleStore（ dataclass ）

- **embeddings**：BaseRagasEmbeddings，用于将 input 转为向量。
- **_examples_list**：`List[Tuple[BaseModel, BaseModel]]`。
- **_embeddings_of_examples**：每条 input 的嵌入向量列表。
- **add_example**：对 input 做 `model_dump_json()` 再 `embed_query`，追加嵌入与 (input, output)。
- **get_examples(data, top_k, threshold)**：对 data 做 `model_dump_json()` 并取嵌入，调用 **get_nearest_examples** 得到下标，再从 _examples_list 取对应元组。
- **get_nearest_examples**（静态）：与 dynamic_few_shot 类似，用 numpy 算余弦相似度，过滤 ≥ threshold，取 top_k 下标。

### 3. FewShotPydanticPrompt(PydanticPrompt, Generic[InputModel, OutputModel])

- **属性**：example_store、top_k_for_examples、threshold_for_examples；__post_init__ 中把 examples 置为空序列。
- **add_example(input, output)**：委托给 example_store.add_example。
- **generate_multiple**：
  - 先从 **example_store.get_examples(data, top_k_for_examples)** 取当前数据对应的少样本，赋给 **self.examples**；
  - 打点 PromptUsageEvent（prompt_type="few_shot"）；
  - 再调用 **super().generate_multiple(...)**，此时父类 to_string 会用到刚赋好的 self.examples。
- **from_pydantic_prompt(cls, pydantic_prompt, embeddings)**：用 InMemoryExampleStore(embeddings) 建库，把 pydantic_prompt.examples 全部 add 进去；新建 FewShotPydanticPrompt(example_store=...)，并拷贝 name、language、instruction、input_model、output_model。

## 与 PydanticPrompt / dynamic_few_shot 的关系

- **PydanticPrompt**：examples 为固定列表，在类或实例上写死。
- **FewShotPydanticPrompt**：examples 每次生成前从 ExampleStore 按相似度刷新，再走 PydanticPrompt 的 to_string + LLM 调用 + 解析流程。
- **DynamicFewShotPrompt**：针对“简单” Prompt（dict in/out），用 SimpleInMemoryExampleStore；FewShotPydanticPrompt 针对 Pydantic 模型，用 InMemoryExampleStore 与 Ragas Embeddings，且与 PydanticPrompt 的 instruction/Schema/examples 格式完全一致。
