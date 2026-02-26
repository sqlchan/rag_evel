# 运行你的第一个实验

本教程将带你使用 `@experiment` 装饰器和本地 CSV 后端，在 Ragas 中运行第一个实验。

## 前置条件

- Python 3.9+
- 已安装 Ragas（参见 [安装](./install.md)）

## Hello World 👋

![](/_static/imgs/experiments_quickstart/hello_world.gif)

### 1. 安装（如尚未安装）

```bash
pip install ragas
```

### 2. 创建 `hello_world.py`

将以下内容复制到新文件并保存为 `hello_world.py`：

```python
import numpy as np
from ragas import Dataset, experiment
from ragas.metrics import MetricResult, discrete_metric


# 定义用于准确率的自定义指标
@discrete_metric(name="accuracy_score", allowed_values=["pass", "fail"])
def accuracy_score(response: str, expected: str):
    result = "pass" if expected.lower().strip() == response.lower().strip() else "fail"
    return MetricResult(value=result, reason=f"Match: {result == 'pass'}")


# 模拟 AI 应用响应的 mock 应用端点
def mock_app_endpoint(**kwargs) -> str:
    return np.random.choice(["Paris", "4", "Blue Whale", "Einstein", "Python"])


# 创建使用 mock 应用端点和准确率指标的实验
@experiment()
async def run_experiment(row):
    response = mock_app_endpoint(query=row.get("query"))
    accuracy = accuracy_score.score(response=response, expected=row.get("expected_output"))
    return {**row, "response": response, "accuracy": accuracy.value}


if __name__ == "__main__":
    import asyncio

    # 内联创建数据集
    dataset = Dataset(name="test_dataset", backend="local/csv", root_dir=".")
    test_data = [
        {"query": "What is the capital of France?", "expected_output": "Paris"},
        {"query": "What is 2 + 2?", "expected_output": "4"},
        {"query": "What is the largest animal?", "expected_output": "Blue Whale"},
        {"query": "Who developed the theory of relativity?", "expected_output": "Einstein"},
        {"query": "What programming language is named after a snake?", "expected_output": "Python"},
    ]

    for sample in test_data:
        dataset.append(sample)
    dataset.save()

    # 运行实验
    _ = asyncio.run(run_experiment.arun(dataset, name="first_experiment"))
```

### 3. 查看生成的文件

```bash
tree .
```

你将看到：

```
├── datasets
│   └── test_dataset.csv
└── experiments
    └── first_experiment.csv
```

### 4. 查看第一个实验的结果

```bash
open experiments/first_experiment.csv
```

输出预览：

![](/_static/imgs/experiments_quickstart/output_first_experiment.png)

## 下一步

- 在 [实验（概念）](../concepts/experimentation.md) 中了解实验背后的概念
- 在 [指标](../concepts/metrics/index.md) 中探索评估指标
