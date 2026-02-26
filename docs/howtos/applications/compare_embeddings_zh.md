---
search:
  exclude: true
---

# 为检索器比较 Embedding

检索器的表现是决定检索增强生成（RAG）系统整体效果的关键因素之一。其中，所用 embedding 的质量会直接影响检索内容的质量。

本教程 notebook 介绍如何用 Ragas 库一步步比较并为自己的数据选出最合适的 embedding。

<figure markdown="span">
![Compare Embeddings](../../_static/imgs/compare-embeddings.jpeg){width="600"}
<figcaption>比较 Embedding</figcaption>
</figure>

## 创建合成测试数据


!!! tip
    Ragas 也支持使用你自己的数据集。参见 [数据准备](../customizations/testgenerator/index_zh.md) 了解如何将自有数据集与 Ragas 配合使用。

Ragas 提供独特的测试生成范式，能为你的检索与生成任务专门创建评估数据集。与传统 QA 生成器不同，Ragas 能从文档语料中生成多种具有挑战性的测试用例。

!!! tip
    更多工作原理请参阅 [测试集生成](../../getstarted/rag_testset_generation_zh.md)。

本教程使用 Semantic Scholar 上与大规模语言模型相关的论文构建 RAG。

```python
from llama_index.core import download_loader
from ragas.testset.evolutions import simple, reasoning, multi_context
from ragas.testset.generator import TestsetGenerator
from langchain_openai import ChatOpenAI
from ragas.embeddings import OpenAIEmbeddings
import openai

SemanticScholarReader = download_loader("SemanticScholarReader")
loader = SemanticScholarReader()
query_space = "large language models"
documents = loader.load_data(query=query_space, limit=100)

# generator with openai models
generator_llm = ChatOpenAI(model="gpt-4o-mini")
critic_llm = ChatOpenAI(model="gpt-4o")
openai_client = openai.OpenAI()
embeddings = OpenAIEmbeddings(client=openai_client)

generator = TestsetGenerator.from_langchain(
    generator_llm,
    critic_llm,
    embeddings
)


distributions = {
    simple: 0.5,
    multi_context: 0.4,
    reasoning: 0.1
}

# generate testset
testset = generator.generate_with_llamaindex_docs(documents, 100,distributions)
test_df = testset.to_pandas()
```

<figure markdown="span">
![testset-output](../../_static/imgs/testset_output.png){width="800"}
<figcaption>测试输出</figcaption>
</figure>

```python
test_questions = test_df['question'].values.tolist()
test_answers = [[item] for item in test_df['answer'].values.tolist()]
```


## 构建你的 RAG

这里使用 llama-index 基于文档构建一个基础 RAG 流水线。目标是从流水线中收集每个测试问题对应的检索上下文和生成答案。Ragas 与多种 RAG 框架集成，便于用 Ragas 进行评估。

!!! note
    使用 LangChain 进行评估的方法请参阅 [langchain 教程](../integrations/_langchain_zh.md)

```python

import nest_asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from langchain.embeddings import HuggingFaceEmbeddings
from ragas.embeddings import OpenAIEmbeddings
import openai
import pandas as pd

nest_asyncio.apply()


def build_query_engine(embed_model):
    vector_index = VectorStoreIndex.from_documents(
        documents, service_context=ServiceContext.from_defaults(chunk_size=512),
        embed_model=embed_model,
    )

    query_engine = vector_index.as_query_engine(similarity_top_k=2)
    return query_engine
```

## 从 Ragas 导入指标

此处导入评估检索器组件所需的指标。

```python
from ragas.metrics import (
    context_precision,
    context_recall,
)

metrics = [
    context_precision,
    context_recall,
]
```

## 评估 OpenAI Embedding

```python
from ragas.llama_index import evaluate

openai_model = OpenAIEmbedding()
query_engine1 = build_query_engine(openai_model)
result = evaluate(query_engine1, metrics, test_questions, test_answers)
```

```python
{'context_precision': 0.2378, 'context_recall': 0.7159}
```

## 评估 Bge Embedding

```python
from ragas.llama_index import evaluate

flag_model = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
query_engine2 = build_query_engine(flag_model)
result = evaluate(query_engine2, metrics, test_questions, test_answers)
```

```python
{'context_precision': 0.2655, 'context_recall': 0.7227}

```

## 对比分数

根据评估结果，在本 RAG 流水线及自有数据上，BGE 模型的 `context_precision` 和 `context_recall` 略优于 OpenAI-Ada 模型。

若需进一步分析，可将结果导出为 pandas：

```python
result_df = result.to_pandas()
result_df.head()
```

<figure markdown="span">
![compare-embeddings-results](../../_static/imgs/compare-emb-results.png){width="800"}
<figcaption>比较 Embedding 结果</figcaption>
</figure>
