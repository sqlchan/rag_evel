# 评估样本

评估样本是用于在特定场景下评估和衡量 LLM 应用性能的单一结构化数据实例。它代表 AI 应用需要处理的单次交互或具体用例。在 Ragas 中，评估样本由 `SingleTurnSample` 和 `MultiTurnSample` 类表示。

## SingleTurnSample

SingleTurnSample 表示用户、LLM 与评估期望结果之间的单轮交互。适用于单问单答的评估，可包含额外上下文或参考信息。

### 示例

以下示例演示如何为基于 RAG 的应用中的单轮交互创建 `SingleTurnSample` 实例。场景中用户提问、AI 作答。我们创建一个包含检索上下文、参考答案和评估量表的 SingleTurnSample 实例。

```python
from ragas import SingleTurnSample

# 用户问题
user_input = "法国的首都是哪里？"

# 检索到的上下文（例如来自知识库或搜索引擎）
retrieved_contexts = ["巴黎是法国的首都和人口最多的城市。"]

# AI 的回复
response = "法国的首都是巴黎。"

# 参考答案（标准答案）
reference = "巴黎"

# 评估量表
rubric = {
    "accuracy": "Correct",
    "completeness": "High",
    "fluency": "Excellent"
}

# 创建 SingleTurnSample 实例
sample = SingleTurnSample(
    user_input=user_input,
    retrieved_contexts=retrieved_contexts,
    response=response,
    reference=reference,
    rubric=rubric
)
```

## MultiTurnSample

MultiTurnSample 表示人、AI 以及可选的工具之间的多轮交互及评估期望结果。适用于表示更复杂交互中的对话智能体以供评估。在 `MultiTurnSample` 中，`user_input` 属性表示共同构成用户与 AI 系统多轮对话的消息序列。这些消息是 `HumanMessage`、`AIMessage` 和 `ToolMessage` 类的实例。

### 示例

以下示例演示如何创建用于评估多轮交互的 `MultiTurnSample` 实例。场景中用户想了解纽约市当前天气，AI 助手将调用天气 API 工具获取信息并回复用户。

```python
from ragas.messages import HumanMessage, AIMessage, ToolMessage, ToolCall

# 用户询问纽约市天气
user_message = HumanMessage(content="纽约市今天天气怎么样？")

# AI 决定使用天气 API 工具获取信息
ai_initial_response = AIMessage(
    content="我来帮你查一下纽约市当前的天气。",
    tool_calls=[ToolCall(name="WeatherAPI", args={"location": "New York City"})]
)

# 工具返回天气信息
tool_response = ToolMessage(content="纽约市今天晴，气温 75°F。")

# AI 向用户给出最终回复
ai_final_response = AIMessage(content="纽约市今天晴，气温 75 华氏度。")

# 将所有消息组合成列表表示对话
conversation = [
    user_message,
    ai_initial_response,
    tool_response,
    ai_final_response
]
```

接着用该对话创建 MultiTurnSample 对象，可包含参考响应和评估量表。

```python
from ragas import MultiTurnSample
# 用于评估的参考响应
reference_response = "向用户提供纽约市当前天气信息。"


# 创建 MultiTurnSample 实例
sample = MultiTurnSample(
    user_input=conversation,
    reference=reference_response,
)
```
