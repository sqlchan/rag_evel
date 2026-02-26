# ragas/dataset_schema.py 功能说明

## 概述
评估用数据结构：单轮/多轮样本、评估数据集、评估结果、标注与批处理（采样、分层、batch）。

## 样本类型
- **BaseSample**: 基类，to_dict（exclude_none）、get_features、to_string。
- **SingleTurnSample**: user_input、retrieved_contexts、reference_contexts、response、reference、rubrics 等单轮字段。
- **MultiTurnSample**: user_input 为 HumanMessage/AIMessage/ToolMessage 列表；reference、reference_tool_calls、rubrics、reference_topics。field_validator 保证 ToolMessage 前必有 AIMessage、且紧跟含 tool_calls 的 AIMessage 或另一 ToolMessage。

## 数据集
- **RagasDataset**: 抽象泛型，samples 列表、validate_samples（同类型）、get_sample_type、to_list/from_list（抽象）、to_hf_dataset/from_hf_dataset、to_pandas/from_pandas、from_dict、to_csv、to_jsonl/from_jsonl。
- **EvaluationDataset**: RagasDataset[SingleTurnSample|MultiTurnSample]，支持 backend/name，__getitem__ 支持 int/slice，is_multi_turn()；from_list 根据 user_input 是否为 list 判断单轮/多轮。

## 评估结果
- **EvaluationResult**: scores（每行每指标）、dataset、binary_columns、cost_cb、traces、ragas_traces、run_id。__post_init__ 中把 scores 转成 _scores_dict（按列）、算 _repr_dict（safe_nanmean）、用 parse_run_traces 解析 ragas_traces 得到 traces。to_pandas 合并 dataset 与 scores；total_tokens/total_cost 委托给 cost_cb。

## 标注
- **PromptAnnotation / SampleAnnotation / MetricAnnotation**: 存储 prompt 输入输出、单样本指标输出、是否接受、target 等；MetricAnnotation.from_json、_process_dataset；SingleMetricAnnotation 支持 to_evaluation_dataset、select、filter、sample（简单或分层）、batch、stratified_batches、get_prompt_annotations，以及未实现的 train_test_split。
