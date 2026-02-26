# 智能体或工具使用

智能体或工具使用工作流可从多个维度评估。以下为可用于评估智能体/工具在给定任务中表现的指标。

## 主题遵循（Topic Adherence）

部署在实际应用中的 AI 应在与用户交互时遵循预定领域，但 LLM 有时会忽略该限制回答通用问题。主题遵循指标评估 AI 在交互中是否保持在预定义领域内，对仅需回答特定领域问题的对话系统尤为重要。

`TopicAdherence` 需要预定义主题集合（通过 `reference_topics` 与 `user_input` 提供），可计算精确率、召回率和 F1。公式与示例见 [agents.md](agents.md)。可用 `mode="precision"` 或 `mode="recall"`。

## 工具调用准确率（Tool call Accuracy）

`ToolCallAccuracy` 衡量 LLM 智能体调用工具与期望工具调用在**顺序与参数**上的准确程度，0–1。

**两种模式**：  
- **严格顺序（默认）**：工具调用顺序必须完全匹配。  
- **灵活顺序**（`strict_order=False`）：顺序不限，适用于可并行调用的场景。  

最终分数 = 参数准确率 × (顺序是否对齐 ? 1 : 0)。示例与 Legacy API 见 [agents.md](agents.md)。

## 工具调用 F1（Tool Call F1）

`ToolCallF1` 基于工具调用的精确率与召回率计算 F1，与期望调用（`reference_tool_calls`）比较，**不考虑顺序**，只考虑工具名与参数是否匹配。适用于 onboarding 与迭代时衡量智能体与期望行为的接近程度。与 Topic Adherence 的区分见 [agents.md](agents.md)。

## 智能体目标准确率（Agent Goal Accuracy）

二元指标：评估 LLM 是否识别并达成用户目标，1 表示达成，0 表示未达成。

- **AgentGoalAccuracyWithReference**：将工作流最终状态与给定参考结果比较。  
- **AgentGoalAccuracyWithoutReference**：无需参考，从对话中推断用户目标与达成结果再比较。  

示例与 Legacy API 见 [agents.md](agents.md)。

### 何时用哪个指标

| 指标 | 适用场景 |
|--------|----------|
| **ToolCallAccuracy** | 关心工具顺序与参数是否完全正确 |
| **ToolCallF1** | 需要工具调用的精确率/召回/F1 |
| **AgentGoalAccuracy** | 只关心结果是否达成，不关心具体调用了哪些工具 |

例如「帮我订一张去巴黎的机票」：若只关心是否订成功，用 `AgentGoalAccuracyWithReference` 更合适。
