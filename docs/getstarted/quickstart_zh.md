# 快速开始：几分钟内运行评估

几分钟内上手 Ragas，用少量命令即可创建完整的评估项目。

## 步骤 1：创建项目

任选一种方式：

=== "uvx（推荐）"
    无需安装。`uvx` 会自动下载并运行 ragas：

    ```sh
    uvx ragas quickstart rag_eval
    cd rag_eval
    ```

=== "先安装 Ragas"
    先安装 ragas，再创建项目：

    ```sh
    pip install ragas
    ragas quickstart rag_eval
    cd rag_eval
    ```

## 步骤 2：安装依赖

安装项目依赖：

```sh
uv sync
```

若偏好 `pip`：

```sh
pip install -e .
```

## 步骤 3：设置 API 密钥

默认情况下，快速开始示例使用 OpenAI。设置好 API 密钥即可开始。也可通过小幅修改使用其他提供商：

=== "OpenAI（默认）"
    ```sh
    export OPENAI_API_KEY="your-openai-key"
    ```

    快速开始项目已配置为使用 OpenAI，无需额外设置。

=== "Anthropic Claude"
    设置 Anthropic API 密钥：

    ```sh
    export ANTHROPIC_API_KEY="your-anthropic-key"
    ```

    然后在 `evals.py` 中更新 LLM 初始化：

    ```python
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

    然后在 `evals.py` 中更新 LLM 初始化：

    **方式一：使用 Google 官方库（推荐）**

    ```python
    import google.generativeai as genai
    from ragas.llms import llm_factory

    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    client = genai.GenerativeModel("gemini-2.0-flash")
    llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
    # 适配器会为 google 提供商自动识别为 "litellm"
    ```

    更多 Gemini 选项与详细配置请参阅 [Google Gemini 集成指南](../howtos/integrations/gemini.md)。

=== "本地模型（Ollama）"
    在本地安装并运行 Ollama，然后在 `evals.py` 中更新 LLM 初始化：

    ```python
    from openai import OpenAI
    from ragas.llms import llm_factory

    # 为 Ollama 创建 OpenAI 兼容客户端
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

## 项目结构

生成的项目包含：

```sh
rag_eval/
├── README.md              # 项目说明
├── pyproject.toml         # 项目配置
├── rag.py                 # 你的 RAG 应用
├── evals.py               # 评估工作流
├── __init__.py            # 使本项目成为 Python 包
└── evals/
    ├── datasets/          # 测试数据文件
    ├── experiments/       # 评估结果
    └── logs/              # 执行日志
```

## 步骤 4：运行评估

运行评估脚本：

```sh
uv run python evals.py
```

若使用 `pip` 安装：

```sh
python evals.py
```

评估将：

- 从 `evals.py` 中的 `load_dataset()` 加载测试数据
- 用测试问题调用你的 RAG 应用
- 对响应进行评估
- 在控制台展示结果
- 将结果保存为 CSV 到 `evals/experiments/` 目录

![](../_static/imgs/results/rag_eval_result.png)

恭喜，你已经有一套完整的评估环境在运行。🎉

---

## 自定义评估

### 添加更多测试用例

在 `evals.py` 中编辑 `load_dataset()`，增加更多测试问题：

```python
from ragas import Dataset

def load_dataset():
    """加载用于评估的测试数据集。"""
    dataset = Dataset(
        name="test_dataset",
        backend="local/csv",
        root_dir=".",
    )

    data_samples = [
        {
            "question": "What is Ragas?",
            "grading_notes": "Ragas is an evaluation framework for LLM applications",
        },
        {
            "question": "How do metrics work?",
            "grading_notes": "Metrics evaluate the quality and performance of LLM responses",
        },
        # 在此添加更多测试用例
    ]

    for sample in data_samples:
        dataset.append(sample)

    dataset.save()
    return dataset
```

### 自定义评估指标

模板中包含用于自定义评估逻辑的 `DiscreteMetric`。可通过以下方式自定义评估：

1. **修改指标提示** - 调整评估标准
2. **调整允许值** - 更新有效输出类别
3. **添加更多指标** - 为不同维度创建额外指标

修改指标示例：

```python
from ragas.metrics import DiscreteMetric
from ragas.llms import llm_factory

my_metric = DiscreteMetric(
    name="custom_evaluation",
    prompt="Evaluate this response: {response} based on: {context}. Return 'excellent', 'good', or 'poor'.",
    allowed_values=["excellent", "good", "poor"],
)
```

## 下一步

- **理解概念**：阅读 [评估简单 LLM 应用](evals.md) 以深入理解
- **自定义指标**：使用简单装饰器 [创建自己的指标](../concepts/metrics/overview/index.md#output-types)
- **生产集成**：将评估 [集成到 CI/CD 流水线](../howtos/index.md)
- **RAG 评估**：使用专用指标 [评估 RAG 系统](rag_eval.md)
- **Agent 评估**：了解 [AI Agent 评估](../howtos/applications/text2sql.md)
- **测试数据生成**：为评估 [生成合成测试数据集](rag_testset_generation.md)

## 获取帮助

- 📚 [完整文档](https://docs.ragas.io/)
- 💬 [加入 Discord 社区](https://discord.gg/5djav8GGNZ)
- 🐛 [反馈问题](https://github.com/vibrantlabsai/ragas/issues)
