# RAG 评估快速入门

`rag_eval` 模板提供完整的 RAG 评估配置，包括自定义指标、数据集管理和实验记录。

## 创建项目

```sh
# Using uvx (no installation required)
uvx ragas quickstart rag_eval
cd rag_eval

# Or with ragas installed
ragas quickstart rag_eval
cd rag_eval
```

## 安装依赖

```sh
uv sync
```

或使用 pip：

```sh
pip install -e .
```

## 设置 API 密钥

=== "OpenAI (默认)"
    ```sh
    export OPENAI_API_KEY="your-openai-key"
    ```

=== "Anthropic Claude"
    ```sh
    export ANTHROPIC_API_KEY="your-anthropic-key"
    ```

    更新 `evals.py`：
    ```python
    from anthropic import Anthropic
    from ragas.llms import llm_factory

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    llm = llm_factory("claude-3-5-sonnet-20241022", provider="anthropic", client=client)
    ```

=== "Google Gemini"
    ```sh
    export GOOGLE_API_KEY="your-google-api-key"
    ```

    更新 `evals.py`：
    ```python
    import google.generativeai as genai
    from ragas.llms import llm_factory

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    client = genai.GenerativeModel("gemini-2.0-flash")
    llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
    ```

=== "本地模型 (Ollama)"
    ```python
    from openai import OpenAI
    from ragas.llms import llm_factory

    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1"
    )
    llm = llm_factory("mistral", provider="openai", client=client)
    ```

## 运行评估

```sh
uv run python evals.py
```

评估将：

1. 从 `load_dataset()` 加载测试数据
2. 用测试问题查询你的 RAG 应用
3. 使用自定义指标评估回答
4. 在控制台展示结果
5. 将结果保存到 `evals/experiments/` 下的 CSV

## 项目结构

```
rag_eval/
├── README.md              # 项目说明
├── pyproject.toml         # 项目配置
├── rag.py                 # RAG 应用实现
├── evals.py               # 评估流程
├── __init__.py            # Python 包标记
└── evals/
    ├── datasets/          # 测试数据文件
    ├── experiments/       # 评估结果 (CSV)
    └── logs/              # 执行日志与 trace
```

## 理解代码

### RAG 应用 (`rag.py`)

简单 RAG 实现，包含：

- **文档存储**：内存文档集合
- **关键词检索**：简单关键词匹配
- **回答生成**：使用 OpenAI API 生成答案
- **追踪**：记录每次查询便于调试

```python
from rag import default_rag_client

# Initialize with OpenAI client
rag_client = default_rag_client(llm_client=openai_client, logdir="evals/logs")

# Query the RAG system
response = rag_client.query("What is Ragas?")
print(response["answer"])
```

### 评估脚本 (`evals.py`)

评估流程：

1. **数据集加载**：创建带问题和评分说明的测试用例
2. **指标定义**：用于 pass/fail 评估的自定义 `DiscreteMetric`
3. **实验执行**：运行查询并评估回答
4. **结果存储**：保存为 CSV 供分析

```python
from ragas import Dataset, experiment
from ragas.metrics import DiscreteMetric

# Define your metric
my_metric = DiscreteMetric(
    name="correctness",
    prompt="Check if the response contains points from grading notes...",
    allowed_values=["pass", "fail"],
)

# Run experiment
@experiment()
async def run_experiment(row):
    response = rag_client.query(row["question"])
    score = my_metric.score(llm=llm, response=response["answer"], ...)
    return {**row, "response": response["answer"], "score": score.value}
```

## 自定义

### 添加测试用例

在 `evals.py` 中编辑 `load_dataset()`：

```python
def load_dataset():
    dataset = Dataset(
        name="test_dataset",
        backend="local/csv",
        root_dir="evals",
    )

    data_samples = [
        {
            "question": "What is Ragas?",
            "grading_notes": "- evaluation framework - LLM applications",
        },
        {
            "question": "How do experiments work?",
            "grading_notes": "- track results - compare runs - store metrics",
        },
        # Add more test cases...
    ]

    for sample in data_samples:
        dataset.append(sample)
    dataset.save()
    return dataset
```

### 修改指标

通过更新指标的 prompt 修改评估标准：

```python
my_metric = DiscreteMetric(
    name="quality",
    prompt="""Evaluate the response quality:

Response: {response}
Expected Points: {grading_notes}

Rate as:
- 'excellent': All points covered with clear explanation
- 'good': Most points covered
- 'poor': Missing key points

Rating:""",
    allowed_values=["excellent", "good", "poor"],
)
```

### 添加多个指标

为不同评估维度创建更多指标：

```python
from ragas.metrics import DiscreteMetric, NumericalMetric

correctness = DiscreteMetric(
    name="correctness",
    prompt="Is the response factually correct? {response}",
    allowed_values=["correct", "incorrect"],
)

relevance = NumericalMetric(
    name="relevance",
    prompt="Rate relevance 1-5: {response} for question: {question}",
    allowed_values=(1, 5),
)
```

### 使用自己的 RAG 系统

用你的生产 RAG 替换示例：

```python
# In evals.py
from your_rag_module import YourRAGClient

rag_client = YourRAGClient(...)

@experiment()
async def run_experiment(row):
    # Call your RAG system
    response = await rag_client.query(row["question"])

    score = my_metric.score(
        llm=llm,
        response=response,
        grading_notes=row["grading_notes"],
    )

    return {
        **row,
        "response": response,
        "score": score.value,
    }
```

## 查看结果

结果以 CSV 形式保存在 `evals/experiments/`。每次实验运行会生成新文件，包含：

- 输入数据（问题、评分说明）
- 模型回答
- 评估分数
- 时间戳

```python
import pandas as pd

# Load results
results = pd.read_csv("evals/experiments/your_experiment.csv")

# Calculate pass rate
pass_rate = (results["score"] == "pass").mean()
print(f"Pass rate: {pass_rate:.1%}")
```

## 下一步

- [改进 RAG 指南](improve_rag_zh.md) - 对比 naive 与 agentic RAG
- [自定义指标](../customizations/metrics/_write_your_own_metric.md) - 编写自己的指标
- [数据集](../../concepts/datasets_zh.md) - 了解数据集管理
- [实验](../../concepts/experimentation_zh.md) - 进阶实验记录
