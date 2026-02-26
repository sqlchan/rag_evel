# ragas/callbacks.py 功能说明

## 概述
与 LangChain 回调体系集成：创建评估链分组、记录链运行轨迹、解析为按行按指标的追踪结构。

## 链分组
- **new_group(name, inputs, callbacks, tags, metadata)**: 用 CallbackManager 启动名为 `name` 的链，返回 (run_manager, group_callback_manager)，用于嵌套子链（如按行、按指标）。

## 类型与模型
- **ChainType**: 枚举——EVALUATION / METRIC / ROW / RAGAS_PROMPT。
- **ChainRun**: Pydantic 模型，表示一次链运行（run_id, parent_run_id, name, inputs, metadata, outputs, children）。
- **ChainRunEncoder**: JSON 序列化时把 UUID、ChainType 转为字符串。

## 追踪器
- **RagasTracer**: BaseCallbackHandler，在 **on_chain_start** 中为每个 run_id 创建 ChainRun 并挂到 parent 的 children；在 **on_chain_end** 中写 outputs；**to_jsons()** 导出所有轨迹的 list。
- **MetricTrace**: 继承 dict，额外带 scores 字典，用于表示单行多指标得分。

## 解析
- **parse_run_traces(traces, parent_run_id)**: 从根 run 开始，按 children 展开为「每行一个 MetricTrace」的列表；每个 MetricTrace 包含各 metric 的 output 以及其下 prompt 的 input/output；若存在多个根则抛 ValueError。
