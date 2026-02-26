# 改进 RAG 快速入门

`improve_rag` 模板演示如何使用真实评估数据对比不同 RAG 方案，包含朴素（单次检索）与智能体式（多步检索）两种 RAG 模式。

## 创建项目

```sh
# 使用 uvx（无需安装）
uvx ragas quickstart improve_rag
cd improve_rag

# 或已安装 ragas 时
ragas quickstart improve_rag
cd improve_rag
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

```sh
export OPENAI_API_KEY="your-openai-key"
```

## 运行评估

### 朴素 RAG 模式（默认）

```sh
uv run python evals.py
```

### 智能体式 RAG 模式

```sh
uv run python evals.py --agentic
```

!!! note "智能体模式要求"
    智能体模式需要 `openai-agents` 包。安装方式：
    ```sh
    pip install openai-agents
    ```

## 可选：MLflow 追踪

若需对 LLM 调用做详细追踪，请先启动 MLflow 再运行评估：

```sh
mlflow ui --port 5000
```

然后运行评估。若 MLflow 服务在运行，追踪会自动发送到 MLflow。

## 项目结构

```
improve_rag/
├── README.md              # 项目说明
├── pyproject.toml         # 项目配置
├── rag.py                 # RAG 实现（朴素与智能体式）
├── evals.py               # 评估流程
├── __init__.py            # Python 包标记
└── evals/
    ├── datasets/          # 测试数据集（hf_doc_qa_eval.csv）
    ├── experiments/      # 评估结果
    └── logs/              # 评估日志
```

## 理解两种 RAG 模式

### 朴素 RAG

朴素模式只做一次检索：

1. **查询** → BM25 检索 top-k 文档
2. **上下文** → 检索到的文档组成上下文
3. **生成** → LLM 基于上下文生成回答

```python
rag = RAG(llm_client=client, retriever=retriever, mode="naive")
result = await rag.query("What is the Diffusers library?")
```

**优点：**

- 简单、速度快
- 延迟可预期
- 成本较低（单次 LLM 调用）

**缺点：**

- 可能因表述不同而漏掉相关文档
- 无查询改写
- 仅限单一检索策略

### 智能体式 RAG

智能体式由智能体控制检索过程：

1. **查询** → 智能体分析问题
2. **检索** → 智能体决定检索什么（可多次检索）
3. **细化** → 可根据结果调整检索
4. **生成** → 智能体综合得到最终答案

```python
rag = RAG(llm_client=client, retriever=retriever, mode="agentic")
result = await rag.query("What command uploads an ESPnet model?")
```

**优点：**

- 可尝试多种检索策略
- 更擅长找到具体技术信息
- 能根据初次结果调整检索

**缺点：**

- 延迟更高（多次 LLM 调用）
- 成本更高
- 行为较难预测

## 评估数据集

模板包含关于 HuggingFace 文档的 `hf_doc_qa_eval.csv`：

| 字段 | 说明 |
|-------|-------------|
| `question` | 关于 HuggingFace 工具的技术问题 |
| `expected_answer` | 标准答案 |

示例问题：

- "What is the default checkpoint used by the sentiment analysis pipeline?"
- "What command is used to upload an ESPnet model?"
- "What is the purpose of the Diffusers library?"

## 代码说明

### RAG 实现（`rag.py`）

#### BM25Retriever

使用 BM25 算法进行文档检索：

```python
class BM25Retriever:
    def __init__(self, dataset_name="m-ric/huggingface_doc"):
        # 加载 HuggingFace 文档
        # 分块以便检索
        # 构建 BM25 索引

    def retrieve(self, query: str, top_k: int = 3):
        # 返回最相关的 top-k 文档
```

#### RAG 类

两种模式统一接口：

```python
class RAG:
    def __init__(self, llm_client, retriever, mode="naive"):
        self.mode = mode
        if mode == "agentic":
            self._setup_agent()

    async def query(self, question: str, top_k: int = 3):
        if self.mode == "naive":
            return await self._naive_query(question, top_k)
        else:
            return await self._agentic_query(question, top_k)
```

### 评估脚本（`evals.py`）

正确性指标将模型回答与期望答案对比：

```python
correctness_metric = DiscreteMetric(
    name="correctness",
    prompt="""Compare the model response to the expected answer...
    Return 'pass' if correct, 'fail' if incorrect.""",
    allowed_values=["pass", "fail"],
)
```

## 自定义

### 更换知识库

用自有文档替换 HuggingFace 文档：

```python
class CustomRetriever:
    def __init__(self, documents: list[str]):
        from langchain_community.retrievers import BM25Retriever
        self.retriever = BM25Retriever.from_texts(documents)

    def retrieve(self, query: str, top_k: int = 3):
        self.retriever.k = top_k
        return self.retriever.invoke(query)
```

### 使用不同模型

在 `evals.py` 中修改模型：

```python
# 使用 GPT-4 提高准确率
rag = RAG(llm_client=client, retriever=retriever, model="gpt-4o")

# 或使用其他提供商
from anthropic import Anthropic
client = Anthropic()
# 注意：非 OpenAI 客户端需修改 rag.py
```

### 添加自定义指标

评估其他维度：

```python
from ragas.metrics import NumericalMetric

completeness = NumericalMetric(
    name="completeness",
    prompt="""How complete is the response (1-5)?
    Question: {question}
    Expected: {expected_answer}
    Response: {response}
    Score:""",
    allowed_values=(1, 5),
)

# 加入实验
result = {
    **row,
    "correctness": correctness_score.value,
    "completeness": completeness.score(...).value,
}
```

### 修改智能体行为

在 `rag.py` 中自定义智能体检索策略：

```python
def _setup_agent(self):
    @function_tool
    def retrieve(query: str) -> str:
        """Custom tool description..."""
        docs = self.retriever.retrieve(query, self.default_k)
        return "\n\n".join([doc.page_content for doc in docs])

    self._agent = Agent(
        name="Custom RAG Assistant",
        instructions="Your custom instructions...",
        tools=[retrieve]
    )
```

## 对比结果

分别运行两种模式并对比：

```sh
# 朴素模式
uv run python evals.py
# 结果保存到 experiments/YYYYMMDD-HHMMSS_naiverag.csv

# 智能体模式
uv run python evals.py --agentic
# 结果保存到 experiments/YYYYMMDD-HHMMSS_agenticrag.csv
```

分析结果：

```python
import pandas as pd

naive = pd.read_csv("evals/experiments/..._naiverag.csv")
agentic = pd.read_csv("evals/experiments/..._agenticrag.csv")

print(f"朴素通过率: {(naive['correctness_score'] == 'pass').mean():.1%}")
print(f"智能体通过率: {(agentic['correctness_score'] == 'pass').mean():.1%}")
```

## 故障排除

### MLflow 告警

若出现 MLflow 追踪失败告警，可以：

1. 启动 MLflow：`mlflow ui --port 5000`
2. 或忽略告警，不启用追踪时评估仍可运行

### 智能体模式不工作

确认已安装 agents 包：

```sh
pip install openai-agents
```

### 首次运行较慢

首次运行会下载 HuggingFace 文档数据集（约 300MB），之后会使用缓存。

## 下一步

- [RAG 评估指南](rag_eval_zh.md) - 更简单的评估配置
- [自定义指标](../customizations/metrics/_write_your_own_metric.md) - 编写自己的指标
- [评估并改进 RAG](../applications/evaluate-and-improve-rag_zh.md) - 生产环境 RAG 评估
