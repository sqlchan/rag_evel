# 指标概述

## 为什么指标重要

无法衡量就无法改进。指标是使迭代成为可能的反馈环。

在 AI 系统中，进展依赖大量实验——每个实验都是关于如何提升性能的假设。但若没有清晰、可靠的指标，就无法区分成功实验（新分数相对旧分数有正向提升）与失败实验。

指标为你指明方向。它们让你能量化改进、发现退化，并将优化工作与用户影响和业务价值对齐。

指标是用于评估 AI 应用性能的量化度量。它们帮助评估应用及其组成组件相对于给定测试数据的表现，为应用开发与部署全流程中的比较、优化和决策提供数值依据。指标在以下方面至关重要：

1. **组件选择**：可用指标在自有数据上比较 AI 应用的不同组件（如 LLM、检索器、智能体配置等），并从多种方案中选出最佳。
2. **错误诊断与调试**：指标帮助定位导致错误或次优表现的部分，便于调试与改进。
3. **持续监控与维护**：指标支持随时间追踪 AI 应用表现，帮助发现并应对数据漂移、模型退化或需求变化等问题。

## AI 应用中的指标类型

### 1. 端到端指标

端到端指标从用户视角评估整体系统表现，将 AI 应用视为黑盒。这些指标仅基于系统最终输出，量化用户关心的关键结果。

例如：

- 答案正确性：衡量检索增强生成（RAG）系统给出的答案是否准确。  
- 引用准确性：评估 RAG 系统引用的参考文献是否被正确识别且相关。

优化端到端指标能带来与用户期望直接对齐的可见改进。

### 2. 组件级指标

组件级指标独立评估 AI 系统的各个部分。它们便于立刻采取针对性改进，但不一定与最终用户满意度直接相关。

例如：

- 检索准确率：衡量 RAG 系统检索相关信息的效果。检索准确率低（如 50%）说明改进该组件可提升整体表现，但单改组件不保证端到端结果更好。

### 3. 业务指标

业务指标将 AI 系统表现与组织目标对齐，并量化可感知的业务结果。这类指标多为滞后指标，在部署一段时间（天/周/月）后计算。

例如：

- 工单转移率：衡量因部署 AI 助手而减少的支持工单比例。

## Ragas 中的指标类型

![按组件评估](../../../_static/imgs/metrics_mindmap.png){width="600"}

指标思维导图

**按底层机制，指标可分为两类**：

     **基于 LLM 的指标**：这类指标底层使用 LLM 进行评估，可能进行一次或多次 LLM 调用得到分数或结果。由于 LLM 对同一输入不一定返回相同结果，这类指标可能具有一定非确定性。另一方面，它们通常更准确、更接近人工评估。

Ragas 中所有基于 LLM 的指标均继承自 `MetricWithLLM` 类。评分前需设置 LLM 对象。  

```python
from ragas.metrics import FactualCorrectness
scorer = FactualCorrectness(llm=evaluation_llm)
```

每个基于 LLM 的指标还配有使用[提示对象](./../../components/prompt_zh.md)编写的提示。你可根据领域和用例自定义这些提示。详见[修改指标中的提示](../../../howtos/customizations/metrics/modifying-prompts-metrics.md)指南。

     **非基于 LLM 的指标**：这类指标底层不使用 LLM 进行评估，具有确定性，可在不调用 LLM 的情况下评估 AI 应用表现。它们依赖传统方法（如字符串相似度、BLEU 分数等），因此与人工评估的相关性通常较低。

Ragas 中所有非基于 LLM 的指标均继承自 `Metric` 类。

**按所评估的数据类型，指标可大致分为**：

     **单轮指标**：基于用户与 AI 的单轮交互评估表现。Ragas 中支持单轮评估的指标均继承自 [SingleTurnMetric][ragas.metrics.base.SingleTurnMetric] 类，使用 `single_turn_ascore` 方法评分，并期望输入为 [Single Turn Sample][ragas.dataset_schema.SingleTurnSample] 对象。

```python
from ragas.metrics import FactualCorrectness

scorer = FactualCorrectness()
await scorer.single_turn_ascore(sample)
```

     **多轮指标**：基于用户与 AI 的多轮交互评估表现。Ragas 中支持多轮评估的指标均继承自 [MultiTurnMetric][ragas.metrics.base.MultiTurnMetric] 类，使用 `multi_turn_ascore` 方法评分，并期望输入为 [Multi Turn Sample][ragas.dataset_schema.MultiTurnSample] 对象。

```python
from ragas.metrics import AgentGoalAccuracy
from ragas import MultiTurnSample

scorer = AgentGoalAccuracy()
await scorer.multi_turn_ascore(sample)
```

### 输出类型

在 Ragas 中，我们按指标产生的输出类型分类，以便理解各指标的行为及结果的解释与聚合方式。三种类型为：

#### 1. 离散型指标

从预定义的类别列表中返回单个值，类别之间无隐含顺序。常见用途包括将输出分为通过/不通过或好/一般/差等。离散型指标可直接接受自定义提示，适合快速自定义评估。

示例：

```python
from ragas.metrics import discrete_metric

@discrete_metric(name="response_quality", allowed_values=["pass", "fail"])
def my_metric(predicted: str, expected: str) -> str:
    return "pass" if predicted.lower() == expected.lower() else "fail"
```

修改现有集合类指标（如 Faithfulness、FactualCorrectness）的提示，请参阅 [修改指标中的提示](../../../howtos/customizations/metrics/modifying-prompts-metrics.md)。

#### 2. 数值型指标

在指定范围内返回整数或浮点数。数值型指标支持均值、求和、众数等聚合，便于统计分析。

```python
from ragas.metrics import numeric_metric

@numeric_metric(name="response_accuracy", allowed_values=(0, 1))
def my_metric(predicted: float, expected: float) -> float:
    return abs(predicted - expected) / max(expected, 1e-5)

my_metric.score(predicted=0.8, expected=1.0)  # 返回浮点值
```

#### 3. 排序型指标

一次评估多个输出，并按给定准则返回排序列表。适用于比较同一流程的多个输出。

```python
from ragas.metrics import ranking_metric
@ranking_metric(name="response_ranking", allowed_values=[0,1])
def my_metric(responses: list) -> list:
    response_lengths = [len(response) for response in responses]
    sorted_indices = sorted(range(len(response_lengths)), key=lambda i: response_lengths[i])
    return sorted_indices

my_metric.score(responses=["short", "a bit longer", "the longest response"])  # 返回索引的排序列表
```

## 指标设计原则

为 AI 应用设计有效指标需遵循一组核心原则，以保证可靠性、可解释性和相关性。Ragas 在设计指标时遵循以下五条原则：

**1. 单一方面**
一个指标只针对 AI 应用表现的某一个具体方面。这样指标既易解释又可执行，能清楚反映所度量的内容。

**2. 直观可解释**
指标应易于理解和解释。清晰直观的指标便于传达结果并得出有意义的结论。

**3. 有效的提示流程**
在使用大语言模型（LLM）开发指标时，采用与人工评估紧密对齐的智能提示流程。将复杂任务拆成更小的子任务并配以专门提示，可提高指标的准确性和相关性。

**4. 鲁棒性**
确保基于 LLM 的指标包含足够的、能反映期望结果的少样本示例，通过提供上下文和指引增强指标的鲁棒性。

**5. 一致的分数范围**
将指标分数归一化或限定在特定范围（如 0 到 1）至关重要，便于不同指标之间的比较，并保持评估框架内的一致性和可解释性。

这些原则为创建不仅有效且实用、有意义的 AI 应用评估指标奠定基础。

## 为应用选择合适的指标

### 1. 优先端到端指标

首先关注反映整体用户满意度的指标。虽然影响满意度的因素很多（如事实正确性、语气、解释深度），初期应集中在能带来最大用户价值的少数维度（例如 RAG 助手中的答案与引用准确性）。

### 2. 保证可解释性

设计足够清晰、便于整个团队理解和推理的指标。例如：

- 文本转 SQL 系统中的执行准确率：生成的 SQL 是否与领域专家编写的标准查询返回完全一致的数据集？

### 3. 强调客观而非主观指标

优先采用客观标准的指标，减少主观判断。可通过团队成员独立标注样本并衡量一致性来评估客观性。高评分者一致性（≥80%）表示更客观。

### 4. 少而强的信号优于多而弱的信号

避免堆砌只能提供弱信号、妨碍清晰决策的指标。应选择较少但信号强、可靠的指标。例如：

- 在对话 AI 中，使用单一指标如目标准确率（用户与 AI 交互的目标是否达成）作为系统表现的强代理，优于多个弱代理（如连贯性、有用性）。

