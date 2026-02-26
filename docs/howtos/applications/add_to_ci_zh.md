---
search:
  exclude: true
---

# 使用 Pytest 将评估加入 CI 流水线

你可以将 Ragas 评估作为持续集成（CI）流水线的一部分，以跟踪 RAG 流水线的定性表现。可将其视为端到端测试套件的一部分，在重大变更和发布前运行。

用法很直接，主要是在调用 `evaluate()` 时把 `in_ci` 参数设为 `True`。这会使 Ragas 在特殊模式下运行，保证指标更可复现，但成本会更高。

可以按下面这样写一个 Pytest 测试：

!!! note
    该数据集已预先填充了参考 RAG 的输出。在测试你自己的系统时，请确保使用待测 RAG 流水线的输出。关于如何构建数据集，请参阅 [使用自有数据构建 HF `Dataset`](./data_preparation_zh.md) 文档。

```python
import pytest
from datasets import load_dataset

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)

def assert_in_range(score: float, value: float, plus_or_minus: float):
    """
    Check if computed score is within the range of value +/- max_range
    """
    assert value - plus_or_minus <= score <= value + plus_or_minus


def test_amnesty_e2e():
    # loading the V2 dataset
    amnesty_qa = load_dataset("vibrantlabsai/amnesty_qa", "english_v2")["eval"]


    result = evaluate(
        amnesty_qa,
        metrics=[answer_relevancy, faithfulness, context_recall, context_precision],
        in_ci=True,
    )
    assert result["answer_relevancy"] >= 0.9
    assert result["context_recall"] >= 0.95
    assert result["context_precision"] >= 0.95
    assert_in_range(result["faithfulness"], value=0.4, plus_or_minus=0.1)
```

## 使用 Pytest Markers 标记 Ragas 端到端测试

由于这些是耗时的端到端测试，可以利用 [Pytest Markers](https://docs.pytest.org/en/latest/example/markers.html) 为测试打上特殊标签。建议为 Ragas 测试使用单独标签，以便在需要时才运行。

在 `conftest.py` 中添加新的 `ragas_ci` 标签：

```python
def pytest_configure(config):
    """
    configure pytest
    """
    # add `ragas_ci`
    config.addinivalue_line(
        "markers", "ragas_ci: Set of tests that will be run as part of Ragas CI"
    )
```

之后即可用 `ragas_ci` 标记所有属于 Ragas CI 的测试。

```python
import pytest
from datasets import load_dataset

from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    context_recall,
    context_precision,
)

def assert_in_range(score: float, value: float, plus_or_minus: float):
    """
    Check if computed score is within the range of value +/- max_range
    """
    assert value - plus_or_minus <= score <= value + plus_or_minus


@pytest.mark.ragas_ci
def test_amnesty_e2e():
    # loading the V2 dataset
    amnesty_qa = load_dataset("vibrantlabsai/amnesty_qa", "english_v2")["eval"]


    result = evaluate(
        amnesty_qa,
        metrics=[answer_relevancy, faithfulness, context_recall, context_precision],
        in_ci=True,
    )
    assert result["answer_relevancy"] >= 0.9
    assert result["context_recall"] >= 0.95
    assert result["context_precision"] >= 0.95
    assert_in_range(result["faithfulness"], value=0.4, plus_or_minus=0.1)
```
