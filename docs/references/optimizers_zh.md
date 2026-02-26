# Optimizers API 参考

Ragas 提供优化器，通过自动优化改进指标提示。本文档介绍可用的优化器类及其配置。

## 概述

优化器利用带真实标签分数的标注数据集优化指标提示，通过以下方式提升准确率：

- **指令优化**：改进提示措辞
- **示例优化**：筛选有效的少样本示例
- **搜索策略**：在提示空间中高效搜索

## 核心类

::: ragas.optimizers
    options:
        members:
            - Optimizer
            - GeneticOptimizer
            - DSPyOptimizer

## GeneticOptimizer

基于简单进化算法的提示指令优化器。

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `max_steps` | `int` | 50 | 最大进化步数 |
| `population_size` | `int` | 10 | 每代种群大小 |
| `mutation_rate` | `float` | 0.2 | 变异概率 |

### 用法

```python
from ragas.optimizers import GeneticOptimizer
from ragas.config import InstructionConfig

optimizer = GeneticOptimizer(
    max_steps=50,
    population_size=10,
)

config = InstructionConfig(llm=llm, optimizer=optimizer)
metric.optimize_prompts(dataset, config)
```

### 工作原理

1. 生成多种提示变体组成的种群
2. 在标注数据集上评估每种变体
3. 选择表现最好的个体
4. 通过交叉与变异产生下一代
5. 重复至达到 max_steps 次迭代

**优点**：实现简单，在数据有限时也可用  
**缺点**：收敛较慢，仅优化指令

## DSPyOptimizer

基于 DSPy [MIPROv2](https://dspy.ai/api/optimizers/MIPROv2/) 算法的高级优化器。

### 参数

| 参数 | 类型 | 默认值 | 说明 |
|-----------|------|---------|-------------|
| `num_candidates` | `int` | 10 | 尝试的提示变体数量 |
| `max_bootstrapped_demos` | `int` | 5 | 自动生成示例的最大数量 |
| `max_labeled_demos` | `int` | 5 | 人工标注示例的最大数量 |
| `init_temperature` | `float` | 1.0 | 探索温度 (0.0-2.0) |

### 用法

```python
from ragas.optimizers import DSPyOptimizer
from ragas.config import InstructionConfig

optimizer = DSPyOptimizer(
    num_candidates=10,
    max_bootstrapped_demos=5,
    max_labeled_demos=5,
)

config = InstructionConfig(llm=llm, optimizer=optimizer)
metric.optimize_prompts(dataset, config)
```

### 工作原理

1. 生成候选提示指令
2. 从数据中自举少样本示例
3. 选择最佳人工标注示例
4. 在数据集上评估所有组合
5. 返回表现最好的配置

更多 DSPy 概念可参考：
- [Signatures](https://dspy.ai/learn/programming/signatures/) - DSPy 的输入/输出规范定义方式
- [Optimizers](https://dspy.ai/learn/optimization/optimizers/) - 改进提示与 LM 权重的算法
- [Modules](https://dspy.ai/learn/programming/modules/) - LLM 程序的构建块

**优点**：效果更好，同时优化指令与示例  
**缺点**：需安装 DSPy，LLM 调用更多

### 安装

[DSPy](https://dspy.ai/) 为可选依赖：

```bash
# 使用 uv（推荐）
uv add "ragas[dspy]"

# 使用 pip
pip install "ragas[dspy]"
```

### 成本估算

每次优化的大致 LLM 调用次数：

```
总调用数 ≈ num_candidates × 30 + max_bootstrapped_demos × 7
```

示例：

- 默认配置 (10, 5, 5)：约 335 次调用
- 节省配置 (5, 2, 3)：约 164 次调用
- 激进配置 (20, 10, 10)：约 670 次调用

## 优化器基类

::: ragas.optimizers.base.Optimizer
    options:
        show_source: false
        members:
            - optimize

## 配置

两种优化器均通过 `InstructionConfig` 使用：

```python
from ragas.config import InstructionConfig

config = InstructionConfig(
    llm=llm,                      # 用于优化的 LLM
    optimizer=optimizer_instance, # 使用的优化器
)

# 与指标一起使用
metric.optimize_prompts(dataset, config)
```

## 数据集格式

优化器需要带真实分数的标注数据集：

```python
from ragas.dataset_schema import (
    PromptAnnotation,
    SampleAnnotation,
    SingleMetricAnnotation
)

# 创建标注样本
prompt_annotation = PromptAnnotation(
    prompt_input={"user_input": "...", "response": "..."},
    prompt_output={"score": 0.9},
    edited_output=None,  # 可选：修正后的输出
)

sample = SampleAnnotation(
    metric_input={"user_input": "...", "response": "..."},
    metric_output=0.9,  # 真实分数
    prompts={"metric_prompt": prompt_annotation},
    is_accepted=True,  # 是否参与优化
)

# 创建数据集
dataset = SingleMetricAnnotation(
    name="metric_name",
    samples=[sample, ...]  # 建议 20-50+ 条样本
)
```

## 损失函数

优化器通过损失函数评估提示质量：

```python
from ragas.losses import MSELoss, HuberLoss

# 均方误差（默认）
loss = MSELoss()

# Huber 损失（对异常值更鲁棒）
loss = HuberLoss(delta=1.0)

# 在配置中使用
config = InstructionConfig(llm=llm, optimizer=optimizer, loss=loss)
```

## 对比

| 特性 | GeneticOptimizer | DSPyOptimizer |
|---------|------------------|---------------|
| 安装 | 内置 | 需安装 `ragas[dspy]` |
| 优化目标 | 仅指令 | 指令 + 示例 |
| 最小数据集规模 | 10+ 条样本 | 20+ 条样本 |
| 典型 LLM 调用 | 100-500 | 200-700 |
| 准确率提升 | +5-8% | +8-12% |
| 适用场景 | 快速优化 | 生产环境指标 |

## 另见

- [DSPy 优化器指南](../howtos/customizations/optimizers/dspy-optimizer.md) - 详细用法
- [指标自定义](../howtos/customizations/metrics/custom-metrics.md) - 创建指标
- [Prompt API 参考](./prompt_zh.md) - 理解提示

## 延伸阅读

**DSPy 文档：**
- [DSPy 官方文档](https://dspy.ai/) - DSPy 完整指南
- [MIPROv2 API 参考](https://dspy.ai/api/optimizers/MIPROv2/) - MIPROv2 详细说明
- [DSPy 优化器概览](https://dspy.ai/learn/optimization/optimizers/) - 所有 DSPy 优化器指南
- [DSPy GitHub 仓库](https://github.com/stanfordnlp/dspy) - 源码与示例

**论文：**
- [Optimizing Instructions and Demonstrations for Multi-Stage Language Model Programs](https://arxiv.org/abs/2406.11695) - MIPROv2 论文
