# 可观测性工具

## Phoenix (Arize)

### 1. 简介

为 RAG 流水线建立基线通常不难，但将其提升到适合生产并保证回答质量往往很难。在选项众多的情况下，为 RAG 选择合适的工具和参数本身就有挑战。本教程分享一套稳健的工作流，帮助你在构建 RAG 时做出正确选择并保证质量。

本文介绍如何结合开源库对 RAG 进行评估、可视化和分析。我们将使用：

- [Ragas](https://docs.ragas.io/en/stable/) 进行合成测试数据生成与评估
- Arize AI 的 [Phoenix](https://docs.arize.com/phoenix) 进行追踪、可视化和聚类分析
- [LlamaIndex](https://docs.llamaindex.ai/en/stable/) 构建 RAG 流水线

为便于说明，我们将使用 arXiv 上关于 prompt 工程的论文数据来构建 RAG 流水线。

ℹ️ 本 notebook 需要 OpenAI API 密钥。

### 2. 安装依赖并导入库

运行下方单元格安装 Git LFS，用于下载数据集。


```python
!git lfs install
```

安装并导入 Python 依赖。


```python
!pip install "ragas<0.1.1" pypdf arize-phoenix "openinference-instrumentation-llama-index<1.0.0" "llama-index<0.10.0" pandas
```


```python
import pandas as pd

# Display the complete contents of DataFrame cells.
pd.set_option("display.max_colwidth", None)
```

### 3. 配置 OpenAI API 密钥

若尚未将 OpenAI API 密钥设为环境变量，请进行设置。


```python
import os
from getpass import getpass
import openai

if not (openai_api_key := os.getenv("OPENAI_API_KEY")):
    openai_api_key = getpass("🔑 Enter your OpenAI API key: ")
openai.api_key = openai_api_key
os.environ["OPENAI_API_KEY"] = openai_api_key
```

### 4. 生成合成测试数据集

为评估整理黄金测试数据集往往耗时、繁琐且成本高，尤其在起步阶段或数据源频繁变化时并不现实。可以通过合成生成高质量数据点再由开发者校验来解决，从而将整理测试数据的时间与精力减少约 90%。

运行下方单元格从 arXiv 下载 prompt 工程论文的 PDF 数据集，并使用 LlamaIndex 读取文档。


```python
!git clone https://huggingface.co/datasets/vibrantlabsai/prompt-engineering-papers
```


```python
from llama_index import SimpleDirectoryReader

dir_path = "./prompt-engineering-papers"
reader = SimpleDirectoryReader(dir_path, num_files_limit=2)
documents = reader.load_data()
```

理想的测试数据集应包含高质量、多样化且与生产分布相近的数据点。Ragas 采用独特的基于进化的合成数据生成范式，生成高质量问题并保证多样性。Ragas 默认使用 OpenAI 模型，你也可以选用任意模型。下面使用 Ragas 生成 100 个数据点。


```python
from ragas.testset import TestsetGenerator
from langchain_openai import ChatOpenAI
from ragas.embeddings import OpenAIEmbeddings
import openai

TEST_SIZE = 25

# generator with openai models
generator_llm = ChatOpenAI(model="gpt-4o-mini")
critic_llm = ChatOpenAI(model="gpt-4o")
openai_client = openai.OpenAI()
embeddings = OpenAIEmbeddings(client=openai_client)

generator = TestsetGenerator.from_langchain(generator_llm, critic_llm, embeddings)

# generate testset
testset = generator.generate_with_llamaindex_docs(documents, test_size=TEST_SIZE)
test_df = testset.to_pandas()
test_df.head()
```

你可以按需调整问题类型分布。测试集准备好后，我们使用 LlamaIndex 构建一个简单的 RAG 流水线。

### 5. 使用 LlamaIndex 构建 RAG 应用

LlamaIndex 是构建 RAG 应用的易用、灵活框架。为简化起见，我们使用默认的 LLM（gpt-3.5-turbo）和嵌入模型（openai-ada-2）。

在后台启动 Phoenix，并对 LlamaIndex 应用进行插桩，使 OpenInference span 和 trace 发送到 Phoenix 并汇总。[OpenInference](https://github.com/Arize-ai/openinference/tree/main/spec) 是建立在 OpenTelemetry 之上的开放标准，用于捕获和存储 LLM 应用执行。它旨在作为一类遥测数据，用于理解 LLM 执行及周边应用上下文（如向量库检索、搜索引擎或 API 等外部工具的使用）。


```python
import phoenix as px
from llama_index import set_global_handler

session = px.launch_app()
set_global_handler("arize_phoenix")
```

构建查询引擎。


```python
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding


def build_query_engine(documents):
    vector_index = VectorStoreIndex.from_documents(
        documents,
        service_context=ServiceContext.from_defaults(chunk_size=512),
        embed_model=OpenAIEmbedding(),
    )
    query_engine = vector_index.as_query_engine(similarity_top_k=2)
    return query_engine


query_engine = build_query_engine(documents)
```

在 Phoenix 中应能看到语料索引时产生的 embedding span。将这些 embedding 导出并保存到 DataFrame，供后续可视化使用。


```python
from phoenix.trace.dsl import SpanQuery

client = px.Client()
corpus_df = px.Client().query_spans(
    SpanQuery().explode(
        "embedding.embeddings",
        text="embedding.text",
        vector="embedding.vector",
    )
)
corpus_df.head()
```

重新启动 Phoenix 以清空已累积的 trace。


```python
px.close_app()
session = px.launch_app()
```

### 6. 评估你的 LLM 应用

Ragas 提供丰富的指标，可用于从组件级和端到端评估 RAG 流水线。

使用 Ragas 时，先构造评估数据集，包含问题、生成答案、检索上下文和标准答案（该问题对应的真实期望答案）。


```python
from datasets import Dataset
from tqdm.auto import tqdm
import pandas as pd


def generate_response(query_engine, question):
    response = query_engine.query(question)
    return {
        "answer": response.response,
        "contexts": [c.node.get_content() for c in response.source_nodes],
    }


def generate_ragas_dataset(query_engine, test_df):
    test_questions = test_df["question"].values
    responses = [generate_response(query_engine, q) for q in tqdm(test_questions)]

    dataset_dict = {
        "question": test_questions,
        "answer": [response["answer"] for response in responses],
        "contexts": [response["contexts"] for response in responses],
        "ground_truth": test_df["ground_truth"].values.tolist(),
    }
    ds = Dataset.from_dict(dataset_dict)
    return ds


ragas_eval_dataset = generate_ragas_dataset(query_engine, test_df)
ragas_evals_df = pd.DataFrame(ragas_eval_dataset)
ragas_evals_df.head()
```

在 Phoenix 中查看 LlamaIndex 应用的 trace。


```python
print(session.url)
```

![LlamaIndex 应用在 Phoenix 中的 trace](https://storage.googleapis.com/arize-phoenix-assets/assets/docs/notebooks/ragas/ragas_trace_slide_over.gif)

我们保存两个 DataFrame：一个包含用于后续可视化的 embedding 数据，另一个包含导出的 trace 和 span，供 Ragas 评估使用。


```python
# dataset containing embeddings for visualization
query_embeddings_df = px.Client().query_spans(
    SpanQuery().explode(
        "embedding.embeddings", text="embedding.text", vector="embedding.vector"
    )
)
query_embeddings_df.head()
```


```python
from phoenix.session.evaluation import get_qa_with_reference

# dataset containing span data for evaluation with Ragas
spans_dataframe = get_qa_with_reference(client)
spans_dataframe.head()
```

Ragas 使用 LangChain 评估 LLM 应用数据。对 LangChain 进行 OpenInference 插桩，以便在评估 LLM 应用时观察内部过程。


```python
from openinference.instrumentation.langchain import LangChainInstrumentor

LangChainInstrumentor().instrument()
```

评估 LLM trace，并以 DataFrame 形式查看评估分数。


```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_correctness,
    context_recall,
    context_precision,
)

evaluation_result = evaluate(
    dataset=ragas_eval_dataset,
    metrics=[faithfulness, answer_correctness, context_recall, context_precision],
)
eval_scores_df = pd.DataFrame(evaluation_result.scores)
```

将评估结果提交到 Phoenix，使其作为 span 上的标注可见。


```python
from phoenix.trace import SpanEvaluations

# Assign span ids to your ragas evaluation scores (needed so Phoenix knows where to attach the spans).
eval_data_df = pd.DataFrame(evaluation_result.dataset)
assert eval_data_df.question.to_list() == list(
    reversed(spans_dataframe.input.to_list())  # The spans are in reverse order.
), "Phoenix spans are in an unexpected order. Re-start the notebook and try again."
eval_scores_df.index = pd.Index(
    list(reversed(spans_dataframe.index.to_list())), name=spans_dataframe.index.name
)

# Log the evaluations to Phoenix.
for eval_name in eval_scores_df.columns:
    evals_df = eval_scores_df[[eval_name]].rename(columns={eval_name: "score"})
    evals = SpanEvaluations(eval_name, evals_df)
    px.Client().log_evaluations(evals)
```

在 Phoenix 中可以看到 Ragas 评估结果作为应用 span 上的标注。


```python
print(session.url)
```

![Ragas 评估作为 span 上的标注显示](https://storage.googleapis.com/arize-phoenix-assets/assets/docs/notebooks/ragas/ragas_evaluation_annotations.gif)

### 7. 可视化与分析 Embedding

[Embedding](https://arize.com/blog-course/embeddings-meaning-examples-and-how-to-compute/) 编码了检索文档与用户查询的语义。它们不仅是 RAG 系统的核心部分，对理解和调试 LLM 应用表现也很有用。

Phoenix 从 RAG 应用获取高维 embedding，降维并聚类为有语义的数据组。然后你可以选择指标（如 Ragas 计算的 faithfulness 或 answer correctness）直观检查应用表现并发现有问题聚类。这种做法的好处是在细粒度且有意义的数据子集上提供指标，便于分析局部表现而不仅是全局表现，也有助于理解应用在哪些查询上表现不佳。

我们将以 embedding 可视化模式重新启动 Phoenix，在测试集上检查应用表现。


```python
query_embeddings_df = query_embeddings_df.iloc[::-1]
assert ragas_evals_df.question.tolist() == query_embeddings_df.text.tolist()
assert test_df.question.tolist() == ragas_evals_df.question.tolist()
query_df = pd.concat(
    [
        ragas_evals_df[["question", "answer", "ground_truth"]].reset_index(drop=True),
        query_embeddings_df[["vector"]].reset_index(drop=True),
        test_df[["evolution_type"]],
        eval_scores_df.reset_index(drop=True),
    ],
    axis=1,
)
query_df.head()
```


```python
query_schema = px.Schema(
    prompt_column_names=px.EmbeddingColumnNames(
        raw_data_column_name="question", vector_column_name="vector"
    ),
    response_column_names="answer",
)
corpus_schema = px.Schema(
    prompt_column_names=px.EmbeddingColumnNames(
        raw_data_column_name="text", vector_column_name="vector"
    )
)
# relaunch phoenix with a primary and corpus dataset to view embeddings
px.close_app()
session = px.launch_app(
    primary=px.Dataset(query_df, query_schema, "query"),
    corpus=px.Dataset(corpus_df.reset_index(drop=True), corpus_schema, "corpus"),
)
```

启动 Phoenix 后，可按以下步骤用所选指标可视化数据：

- 选择 `vector` embedding，
- 选择 `Color By > dimension`，再选择要着色的维度（例如按 Ragas 的 faithfulness 或 answer correctness 等着色），
- 在 `metric` 下拉框中选择指标，按聚类查看聚合指标。

![检查 embedding 聚类、查看聚合指标、按所选指标着色](https://storage.googleapis.com/arize-phoenix-assets/assets/docs/notebooks/ragas/ragas_correctness_clusters.gif)

### 8. 小结

你已经使用 Ragas 和 Phoenix 构建并评估了 LlamaIndex 查询引擎。简要回顾如下：

- 使用 Ragas：引导生成测试集，并计算 faithfulness、answer correctness 等指标评估 LlamaIndex 查询引擎。
- 使用 OpenInference：对查询引擎插桩，观察 LlamaIndex 与 Ragas 的内部执行。
- 使用 Phoenix：收集 span 与 trace、导入评估便于检查，并可视化嵌入的查询与检索文档以定位表现较差的区域。

本 notebook 仅是对 Ragas 与 Phoenix 能力的入门介绍。更多内容请参阅 [Ragas](https://docs.ragas.io/en/stable/) 与 [Phoenix 文档](https://docs.arize.com/phoenix/)。

若觉得本教程有用，欢迎在 GitHub 点 ⭐：

- [Ragas](https://github.com/vibrantlabsai/ragas)
- [Phoenix](https://github.com/Arize-ai/phoenix)
- [OpenInference](https://github.com/Arize-ai/openinference)

## LangSmith

[LangSmith](https://docs.smith.langchain.com/) 是用于增强基于大语言模型（LLM）应用的开发与部署的高级工具。它提供追踪、分析和优化 LLM 工作流的完整框架，便于开发者管理应用内的复杂交互。

本教程说明如何使用 LangSmith 记录 Ragas 评估的 trace。由于 Ragas 基于 LangChain 构建，只需配置 LangSmith，即可自动记录 trace。

### 1. 配置 LangSmith

配置 LangSmith 时，请设置以下环境变量（详见 [LangSmith 文档](https://docs.smith.langchain.com/#quick-start)）：

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
export LANGCHAIN_API_KEY=<your-api-key>
export LANGCHAIN_PROJECT=<your-project>  # 未设置时默认为 "default"
```

### 2. 获取数据集

创建评估数据集或评估实例时，请确保术语与 `SingleTurnSample` 或 `MultiTurnSample` 所用 schema 一致。


```python
from ragas import EvaluationDataset


dataset = [
    {
        "user_input": "Which CEO is widely recognized for democratizing AI education through platforms like Coursera?",
        "retrieved_contexts": [
            "Andrew Ng, CEO of Landing AI, is known for his pioneering work in deep learning and for democratizing AI education through Coursera."
        ],
        "response": "Andrew Ng is widely recognized for democratizing AI education through platforms like Coursera.",
        "reference": "Andrew Ng, CEO of Landing AI, is known for his pioneering work in deep learning and for democratizing AI education through Coursera.",
    },
    # ... 更多样本
]

evaluation_dataset = EvaluationDataset.from_list(dataset)
```

### 3. 追踪 Ragas 指标

在数据集上运行 Ragas 评估后，trace 会出现在 LangSmith 仪表盘中指定项目名或 "default" 下。


```python
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness

llm = ChatOpenAI(model="gpt-4o-mini")
evaluator_llm = LangchainLLMWrapper(llm)

result = evaluate(
    dataset=evaluation_dataset,
    metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
    llm=evaluator_llm,
)

result
```

输出示例
```
Evaluating:   0%|          | 0/15 [00:00<?, ?it/s]

{'context_recall': 1.0000, 'faithfulness': 0.9333, 'factual_correctness': 0.8520}
```

### 4. LangSmith 仪表盘
![jpeg](./../_static/langsmith_dashboard.png)
