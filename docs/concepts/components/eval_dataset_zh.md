# 评估数据集

评估数据集是一组同质的[数据样本](eval_sample_zh.md)，用于评估 AI 应用的性能与能力。在 Ragas 中，评估数据集由 `EvaluationDataset` 类表示，用于以结构化方式组织和管理评估用数据样本。

- [概述](#概述)
- [从 SingleTurnSamples 创建评估数据集](#从-singleturnsamples-创建评估数据集)
- [从 Hugging Face Datasets 加载评估数据集](#从-hugging-face-datasets-加载评估数据集)

## 概述

### 评估数据集的结构

评估数据集由以下部分组成：

- **样本**：一组 [SingleTurnSample](eval_sample_zh.md#singleturnsample) 或 [MultiTurnSample](eval_sample_zh.md#multiturnsample) 实例。每个样本代表一次唯一交互或场景。
- **一致性**：数据集中所有样本应为同一类型（全部单轮或全部多轮），以保持评估一致性。

### 构建有效评估数据集的指南

- **明确目标**：确定要评估的 AI 应用方面以及要测试的场景。收集能反映这些目标的数据样本。
- **收集代表性数据**：确保数据集覆盖多样化的场景、用户输入和期望响应，以全面评估 AI 应用。可通过多种来源收集数据或[生成合成数据](./../../howtos/customizations/index.md#testset-generation)实现。
- **质量与规模**：在保证足够样本以得出有统计意义的结论与避免数据量过大之间取得平衡。确保数据高质量并准确反映要评估的真实场景。

## 从 SingleTurnSamples 创建评估数据集

本例演示如何用多个 `SingleTurnSample` 实例创建 EvaluationDataset，包括创建单个样本、组装成数据集以及对数据集进行基本操作。

**步骤 1：** 导入所需类

首先从模块导入 SingleTurnSample 和 EvaluationDataset 类。

```python
from ragas import SingleTurnSample, EvaluationDataset
```

**步骤 2：** 创建单个样本

创建若干表示各评估样本的 SingleTurnSample 实例。

```python
# 样本 1
sample1 = SingleTurnSample(
    user_input="德国的首都是哪里？",
    retrieved_contexts=["柏林是德国的首都和最大城市。"],
    response="德国的首都是柏林。",
    reference="柏林",
)

# 样本 2
sample2 = SingleTurnSample(
    user_input="《傲慢与偏见》是谁写的？",
    retrieved_contexts=["《傲慢与偏见》是简·奥斯汀的小说。"],
    response="《傲慢与偏见》由简·奥斯汀所著。",
    reference="简·奥斯汀",
)

# 样本 3
sample3 = SingleTurnSample(
    user_input="水的化学式是什么？",
    retrieved_contexts=["水的化学式为 H2O。"],
    response="水的化学式是 H2O。",
    reference="H2O",
)
```

**步骤 3：** 创建 EvaluationDataset

传入 SingleTurnSample 实例列表创建 EvaluationDataset。

```python
dataset = EvaluationDataset(samples=[sample1, sample2, sample3])
```

## 从 Hugging Face Datasets 加载评估数据集

实践中，你可能需要从已有数据源（如 Hugging Face Datasets）加载评估数据集。以下示例演示如何从 Hugging Face 数据集加载并转换为 EvaluationDataset 实例。

确保数据集中包含评估所需字段，如用户输入、检索上下文、响应和参考答案。

```python
from datasets import load_dataset
dataset = load_dataset("vibrantlabsai/amnesty_qa","english_v3")
```

将数据集加载为 Ragas 的 EvaluationDataset 对象。

```python
from ragas import EvaluationDataset

eval_dataset = EvaluationDataset.from_hf_dataset(dataset["eval"])
```
