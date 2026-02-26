# ragas/messages.py 功能说明

## 概述
多轮对话与工具调用的消息模型（Pydantic）：基类 Message、HumanMessage/AIMessage/ToolMessage、ToolCall；用于 MultiTurnSample.user_input 及展示。

## Message
- **content**: str；**metadata**: 可选字典。

## ToolCall
- **name**: 工具名；**args**: 参数字典。

## HumanMessage
- **type**: 字面量 "human"；**pretty_repr()**: "Human: {content}"。

## ToolMessage
- **type**: "tool"；**pretty_repr()**: "ToolOutput: {content}"。

## AIMessage
- **type**: "ai"；**tool_calls**: 可选 ToolCall 列表；**metadata** 可选。
- **to_dict()**: content 无 tool_calls 时为字符串，否则为 {text, tool_calls}；返回 {content, type}。
- **pretty_repr()**: 先输出 "AI: content"，若有 tool_calls 再逐条 "Tools: name: args"。
