# ragas/evaluation.py 功能说明

## 概述
评估主流程：校验数据集与指标、注入 LLM/Embeddings、按行提交单轮/多轮打分任务、收集结果并组装 EvaluationResult；支持同步 evaluate 与异步 aevaluate。

## aevaluate（异步核心）
- 校验 dataset 非空、metrics 为 list 且元素为 Metric；默认指标为 answer_relevancy、context_precision、faithfulness、context_recall。
- HuggingFace Dataset 先 remap_column_names、convert_v1_to_v2_dataset，再转 EvaluationDataset；然后 validate_required_columns、validate_supported_metrics。
- Langchain LLM/Embeddings 包装成 LangchainLLMWrapper / LangchainEmbeddingsWrapper。
- 遍历 metrics：AspectCritic 记入 binary_metrics；MetricWithLLM/MetricWithEmbeddings 未设置时用全局或默认（无 LLM 时用 OpenAI gpt-4o-mini）；AnswerCorrectness 未设置 answer_similarity 时记录索引；对每个 metric 调用 init(run_config)。
- 创建 Executor，注册 RagasTracer 与可选的 CostCallbackHandler；new_group 建评估链，对每行 new_group 建 row 链，按 SingleTurnSample/MultiTurnSample 提交 metric.single_turn_ascore 或 metric.multi_turn_ascore。
- 若 return_executor 为 True 则直接返回 Executor；否则 await executor.aresults()，按行按指标组装 scores，结束 row/evaluation 链，构造 EvaluationResult（含 tracer.traces、run_id），finally 中恢复 metric 的 llm/embeddings/answer_similarity 并 flush analytics。

## evaluate（同步入口）
- 标记弃用，建议用 @experiment。根据 allow_nest_asyncio 选择 asyncio.run 或 async_utils.run（内部可 apply_nest_asyncio）执行 aevaluate 的包装协程。
