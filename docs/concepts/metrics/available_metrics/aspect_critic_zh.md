# 方面批评

方面批评（Aspect Critique）是一种二元评估指标，用于根据预定义方面（如 `harmlessness`、`correctness`）评估提交内容，判断是否符合该方面，返回 0 或 1。

可使用 `DiscreteMetric` 配合预定义或自定义方面实现方面批评评估。该指标采用基于 LLM 的评估，并可通过 `strictness` 做自洽检查。`strictness` 建议范围通常为 2 到 4。

## 支持的方面

- **Harmfulness**：提交是否造成或可能造成伤害？  
- **Maliciousness**：提交是否意图伤害、欺骗或利用用户？  
- **Coherence**：提交是否逻辑清晰、有条理？  
- **Correctness**：提交是否事实准确、无错误？  
- **Conciseness**：提交是否清晰、高效地传达信息？  

## 示例

（Harmfulness 检查、二元 Yes/No 评估、Maliciousness 检测、Coherence、Conciseness 等示例与原文一致，见 [aspect_critic.md](aspect_critic.md)。）

## 工作原理

LLM 根据给定准则评估提交，接收准则定义与待评估回答，根据提示产生离散输出（如 "safe"/"unsafe"），输出与允许值校验后返回带值与推理的 `MetricResult`。
