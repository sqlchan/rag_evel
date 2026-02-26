# 评估简单 LLM 应用

本指南旨在说明使用 `ragas` 测试和评估 LLM 应用的简单工作流。假定你对 AI 应用构建与评估仅有基础了解。安装 `ragas` 请参考 [安装说明](./install.md)。

!!! tip "获取可运行示例"
    最快的方式是用 quickstart 命令创建项目并查看这些概念的实际效果：

    === "uvx（推荐）"
        ```sh
        uvx ragas quickstart rag_eval
        cd rag_eval
        uv sync
        ```

    === "先安装 Ragas"
        ```sh
        pip install ragas
        ragas quickstart rag_eval
        cd rag_eval
        uv sync
        ```

    这会生成一个包含示例代码的完整项目。可结合本指南理解生成代码在做什么。开始吧！

## 项目结构

生成的项目结构如下：

```sh
rag_eval/
├── README.md             # 项目说明与配置步骤
├── pyproject.toml        # uv 与 pip 的项目配置
├── evals.py              # 你的评估工作流
├── rag.py                # 你的 RAG/LLM 应用
├── __init__.py           # 使本项目成为 Python 包
└── evals/                # 评估产物
    ├── datasets/         # 测试数据文件（可选）
    ├── experiments/      # 运行评估的结果（CSV 保存在此）
    └── logs/             # 评估执行日志
```

**重点文件：**

- **`evals.py`** - 包含数据集加载与评估逻辑的评估工作流
- **`rag.py`** - 你的 RAG/LLM 应用代码（查询引擎、检索等）

## 理解代码

在生成项目的 `evals.py` 中，你会看到主要工作流模式：

1. **加载数据集** - 使用 `SingleTurnSample` 定义测试用例
2. **查询 RAG 系统** - 从你的应用获取响应
3. **评估响应** - 根据参考答案验证响应
4. **展示结果** - 在控制台显示评估摘要
5. **保存结果** - 自动保存为 CSV 到 `evals/experiments/` 目录

模板提供可自定义的模块化函数：

```python
from ragas.dataset_schema import SingleTurnSample
from ragas import EvaluationDataset

def load_dataset():
    """加载用于评估的测试数据集。"""
    data_samples = [
        SingleTurnSample(
            user_input="What is Ragas?",
            response="",  # 将由 RAG 查询填充
            reference="Ragas is an evaluation framework for LLM applications",
            retrieved_contexts=[],
        ),
        # 添加更多测试用例...
    ]
    return EvaluationDataset(samples=data_samples)
```

你可以用 [指标](../concepts/metrics/available_metrics/index.md) 和更复杂的评估逻辑进行扩展。更多内容见 [Ragas 中的评估](../concepts/evaluation/index.md)。

### 选择 LLM 提供商

快速开始项目默认在 `_init_clients()` 中初始化 OpenAI LLM。你可以通过 `llm_factory` 轻松切换到任意提供商：

=== "OpenAI"
    设置 OpenAI API 密钥：

    ```sh
    export OPENAI_API_KEY="your-openai-key"
    ```

    在 `evals.py` 的 `_init_clients()` 中：

    ```python
    from openai import OpenAI
    from ragas.llms import llm_factory

    client = OpenAI()
    llm = llm_factory("gpt-4o", client=client)
    ```

    快速开始项目中已配置好！

=== "Anthropic Claude"
    设置 Anthropic API 密钥：

    ```sh
    export ANTHROPIC_API_KEY="your-anthropic-key"
    ```

    在 `evals.py` 的 `_init_clients()` 中：

    ```python
    import os
    from anthropic import Anthropic
    from ragas.llms import llm_factory

    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    llm = llm_factory("claude-3-5-sonnet-20241022", provider="anthropic", client=client)
    ```

=== "Google Gemini"
    配置 Google 凭证：

    ```sh
    export GOOGLE_API_KEY="your-google-api-key"
    ```

    在 `evals.py` 的 `_init_clients()` 中：

    ```python
    import os
    import google.generativeai as genai
    from ragas.llms import llm_factory

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    client = genai.GenerativeModel("gemini-2.0-flash")
    llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
    ```

=== "本地模型（Ollama）"
    在本地安装并运行 Ollama，然后在 `evals.py` 的 `_init_clients()` 中：

    ```python
    from openai import OpenAI
    from ragas.llms import llm_factory

    client = OpenAI(
        api_key="ollama",  # Ollama 不需要真实密钥
        base_url="http://localhost:11434/v1"
    )
    llm = llm_factory("mistral", provider="openai", client=client)
    ```

=== "自定义 / 其他提供商"
    适用于任何提供 OpenAI 兼容 API 的 LLM：

    ```python
    from openai import OpenAI
    from ragas.llms import llm_factory

    client = OpenAI(
        api_key="your-api-key",
        base_url="https://your-api-endpoint"
    )
    llm = llm_factory("model-name", provider="openai", client=client)
    ```

    更多细节请参阅 [LLM 集成](../concepts/metrics/index.md)。

### 使用预置指标

`ragas` 提供常见评估任务的预置指标。例如 [Aspect Critique](../concepts/metrics/available_metrics/aspect_critic.md) 使用 `DiscreteMetric` 评估输出的任意维度：

```python
import asyncio
from openai import AsyncOpenAI
from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory

# 配置评估用 LLM
client = AsyncOpenAI()
evaluator_llm = llm_factory("gpt-4o", client=client)

# 创建自定义维度评估器
metric = DiscreteMetric(
    name="summary_accuracy",
    allowed_values=["accurate", "inaccurate"],
    prompt="""Evaluate if the summary is accurate and captures key information.

Response: {response}

Answer with only 'accurate' or 'inaccurate'."""
)

# 对你的应用输出打分
async def main():
    score = await metric.ascore(
        llm=evaluator_llm,
        response="The summary of the text is..."
    )
    print(f"Score: {score.value}")  # 'accurate' 或 'inaccurate'
    print(f"Reason: {score.reason}")


if __name__ == "__main__":
    asyncio.run(main())
```

此类预置指标可避免从零编写评估逻辑。可浏览 [所有可用指标](../concepts/metrics/available_metrics/index.md)。

!!! info
    `ragas` 中还有许多其他类型的指标（带或不带 `reference`），若都不满足需求也可以自定义。更多内容请查看 [指标详解](../concepts/metrics/index.md)。

### 在数据集上评估

在快速开始项目中，`load_dataset()` 会创建包含多个样本的测试数据：

```python
from ragas import Dataset

# 创建包含多个测试样本的数据集
dataset = Dataset(
    name="test_dataset",
    backend="local/csv",  # 也可使用 JSONL、Google Drive 或 in-memory
    root_dir=".",
)

# 向数据集添加样本
data_samples = [
    {
        "user_input": "What is ragas?",
        "response": "Ragas is an evaluation framework...",
        "expected": "Ragas provides objective metrics..."
    },
    {
        "user_input": "How do metrics work?",
        "response": "Metrics score your application...",
        "expected": "Metrics evaluate performance..."
    },
]

for sample in data_samples:
    dataset.append(sample)

# 保存到磁盘
dataset.save()
```

这样就有多个测试用例，而不是一次只评估一个样本。更多内容见 [数据集与实验](../concepts/components/eval_dataset.md)。

生成的项目在 `evals/datasets/` 下包含示例数据，可编辑这些文件以添加更多测试用例。

### 需要借助评估改进 AI 应用？

过去两年里，我们通过评估帮助了许多 AI 应用改进。

我们正在把这些经验沉淀成产品，用评估循环替代“感觉好不好”的检查，让你更专注于把 AI 应用做好。

若你希望借助评估改进和扩展 AI 应用：

🔗 预约 [时段](https://bit.ly/3EBYq4J) 或发邮件：[founders@vibrantlabs.com](mailto:founders@vibrantlabs.com)。

![](../_static/ragas_app.gif)

## 下一步

- [评估简单 RAG 应用](rag_eval.md)
