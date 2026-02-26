# ragas/config.py 功能说明

## 概述
Prompt/Instruction 优化相关配置：Demonstration（示例选择）与 Instruction（指令优化）的 Pydantic 配置模型。

## DemonstrationConfig
- **embedding**: 必须为 BaseRagasEmbeddings 实例，用于示例检索或相似度计算。
- **enabled**: 是否启用示例，默认 True。
- **top_k**: 选取 Top-K 示例，默认 3。
- **threshold**: 相似度阈值，默认 0.7。
- **technique**: "random" 或 "similarity"，默认 "similarity"。
- 通过 field_validator 校验 embedding 类型。

## InstructionConfig
- **llm**: BaseRagasLLM，用于生成或评估指令。
- **enabled**: 是否启用指令优化，默认 True。
- **loss**: 可选 Loss 实例，用于优化目标。
- **optimizer**: 优化器，默认 GeneticOptimizer()。
- **optimizer_config**: 传给优化器的参数字典，默认 DEFAULT_OPTIMIZER_CONFIG（如 max_steps: 100）。

## 依赖
依赖 ragas.embeddings.base、ragas.llms.base、ragas.losses、ragas.optimizers（GeneticOptimizer, Optimizer）。
