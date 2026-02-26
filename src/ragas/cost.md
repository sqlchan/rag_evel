# ragas/cost.py 功能说明

## 概述
基于 LangChain 回调的 Token 用量统计与成本计算：解析不同厂商的 LLM 返回、汇总用量、按单价算总成本。

## TokenUsage
- **input_tokens / output_tokens / model**: 单次调用的输入/输出 token 数与模型名。
- **__add__**: 同模型可相加，否则抛 ValueError。
- **cost(cost_per_input_token, cost_per_output_token)**: 计算单次调用成本；未传 output 单价时与 input 相同。
- **is_same_model**: 判断是否同模型（含两者均为 None）。

## 解析器
- **get_token_usage_for_openai**: 从 llm_output 取 token_usage.prompt_tokens / completion_tokens、model_name。
- **get_token_usage_for_anthropic**: 从每条 ChatGeneration 的 response_metadata 取 usage.input_tokens / output_tokens、model。
- **get_token_usage_for_bedrock**: 从 response_metadata 取 usage.prompt_tokens / completion_tokens、model_id。
- **get_token_usage_for_azure_ai**: 从 llm_output 取 token_usage.input_tokens / output_tokens、model_name。
均使用 ragas.utils.get_from_dict 做安全取值。

## CostCallbackHandler
- **on_llm_end**: 每次 LLM 结束时用注入的 token_usage_parser 解析并追加到 usage_data。
- **total_cost**: 按 model 汇总 TokenUsage；若仅一个模型且未提供 per_model_costs，则用 cost_per_input_token / cost_per_output_token；否则用 per_model_costs 字典 (model -> (input_price, output_price)) 计算总成本；无任何成本配置时抛 ValueError。
- **total_tokens**: 按模型汇总后，单模型返回单个 TokenUsage，多模型返回列表。
