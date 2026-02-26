# 智能体评估快速入门

`agent_evals` 模板提供评估解决数学问题的 AI 智能体的环境，使用正确性类指标。

## 创建项目

```sh
ragas quickstart agent_evals
cd agent_evals
```

## 安装依赖

```sh
uv sync
```

## 设置 API 密钥

```sh
export OPENAI_API_KEY="your-openai-key"
```

## 运行评估

```sh
uv run python evals.py
```

## 项目结构

```
agent_evals/
├── README.md              # 项目说明
├── pyproject.toml         # 项目配置
├── agent.py               # 数学求解智能体实现
├── evals.py               # 评估流程
├── __init__.py            # Python 包标记
└── evals/
    ├── datasets/          # 测试数据集
    ├── experiments/       # 评估结果
    └── logs/              # 执行日志
```

## 评估内容

该模板评估 AI 智能体求解数学表达式的能力：

- **智能体**：使用工具逐步求解数学题
- **测试用例**：如 `(2 + 3) * (6 - 2)`、`100 / 5 + 3 * 2` 等表达式
- **指标**：二值正确性（正确为 1.0，错误为 0.0）

## 代码说明

### 智能体（`agent.py`）

实现带计算器工具的数学求解智能体：

```python
from agent import get_default_agent

math_agent = get_default_agent()
result = math_agent.solve("15 - 3 / 4")
```

### 评估（`evals.py`）

在多种数学题上测试智能体：

```python
@numeric_metric(name="correctness", allowed_values=(0.0, 1.0))
def correctness_metric(prediction: float, actual: float):
    result = 1.0 if abs(prediction - actual) < 1e-5 else 0.0
    return MetricResult(value=result, reason=f"Prediction: {prediction}, Actual: {actual}")
```

## 下一步

- [LlamaIndex 智能体评估](llamaIndex_agent_evals_zh.md) - 评估 LlamaIndex 智能体
- [自定义指标](../customizations/metrics/_write_your_own_metric_zh.md) - 编写自己的指标
