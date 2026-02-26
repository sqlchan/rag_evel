---
search:
  exclude: true
---

# 使用 Ragas 评估比较 LLM

检索增强生成（RAG）系统中使用的 LLM 会显著影响生成结果的质量。对不同 LLM 的生成结果进行评估，有助于为特定场景选择合适的模型。

本教程介绍如何用 Ragas 库一步步比较并为自己的数据选出最合适的 LLM。

<figure markdown="span">
![Compare LLMs](../../_static/imgs/compare-llms-front.jpeg){width="800"}
<figcaption>比较 LLM</figcaption>
</figure>



## 创建合成测试数据


!!! tip
    Ragas 也支持使用你自己的数据集。参见 [数据准备](./data_preparation.md) 了解如何将自有数据集与 Ragas 配合使用。

Ragas 提供独特的测试生成范式，能为你的检索与生成任务专门创建评估数据集。与传统 QA 生成器不同，Ragas 能从文档语料中生成多种具有挑战性的测试用例。

!!! tip
    更多工作原理请参阅 [测试集生成](../../concepts/test_data_generation/index_zh.md)。

本教程使用 Arxiv 上与大规模语言模型相关的论文构建 RAG。

!!! note
    建议使用 Testset 生成器生成 50+ 条样本以获得更好结果

```python
import os
from llama_index import download_loader, SimpleDirectoryReader
from ragas.testset import TestsetGenerator
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

os.environ['OPENAI_API_KEY'] = 'Your OPEN AI key'

# load documents
reader = SimpleDirectoryReader("./arxiv-papers/",num_files_limit=30)
documents = reader.load_data()

# generator with openai models
generator_llm = ChatOpenAI(model="gpt-4o-mini")
critic_llm = ChatOpenAI(model="gpt-4o")
embeddings = OpenAIEmbeddings()

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
testset = generator.generate_with_llama_index_docs(documents, 100,distributions)
testset.to_pandas()
```

<p align="left">
<img src="../../_static/imgs/compare-llms-testset.png" alt="test-outputs" width="800" height="600" />
</p>

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
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.llms import HuggingFaceInferenceAPI
from llama_index.embeddings import HuggingFaceInferenceAPIEmbedding
import pandas as pd

nest_asyncio.apply()


def build_query_engine(llm):
    vector_index = VectorStoreIndex.from_documents(
        documents, service_context=ServiceContext.from_defaults(chunk_size=512, llm=llm),
        embed_model=HuggingFaceInferenceAPIEmbedding,
    )

    query_engine = vector_index.as_query_engine(similarity_top_k=2)
    return query_engine

# Function to evaluate as Llama index does not support async evaluation for HFInference API
def generate_responses(query_engine, test_questions, test_answers):
  responses = [query_engine.query(q) for q in test_questions]

  answers = []
  contexts = []
  for r in responses:
    answers.append(r.response)
    contexts.append([c.node.get_content() for c in r.source_nodes])
  dataset_dict = {
        "question": test_questions,
        "answer": answers,
        "contexts": contexts,
  }
  if test_answers is not None:
    dataset_dict["ground_truth"] = test_answers
  ds = Dataset.from_dict(dataset_dict)
  return ds
```

## 从 Ragas 导入指标

此处导入评估生成/检索组件所需的指标。

```python
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    answer_correctness,
)

metrics = [
    faithfulness,
    answer_relevancy,
    answer_correctness,
]
```

## 评估 Zephyr 7B Alpha LLM

第一个 LLM 使用 HuggingFace 的 [zephyr-7b-alpha](https://huggingface.co/HuggingFaceH4/zephyr-7b-alpha)。通过 HuggingFaceInferenceAPI 调用该模型生成答案。HuggingFaceInferenceAPI 可免费使用，可在 [HuggingFaceToken](https://huggingface.co/docs/hub/security-tokens) 中配置 token。

```python
# Use zephyr model using HFInference API
zephyr_llm = HuggingFaceInferenceAPI(
    model_name="HuggingFaceH4/zephyr-7b-alpha",
    token="Your Hugging Face token"
)
query_engine1 = build_query_engine(zephyr_llm)
result_ds = generate_responses(query_engine1, test_questions, test_answers)
result_zephyr = evaluate(
    result_ds,
    metrics=metrics,
)

result_zephyr
```

```python
{'faithfulness': 0.8365, 'answer_relevancy': 0.8831, 'answer_correctness': 0.6605}
```

## 评估 Falcon-7B-Instruct LLM

第二个评估模型为 [Falcon-7B-Instruct](https://huggingface.co/tiiuae/falcon-7b-instruct)，同样可通过 HuggingFaceInferenceAPI 使用。

```python
falcon_llm = HuggingFaceInferenceAPI(
    model_name="tiiuae/falcon-7b-instruct",
    token="Your Huggingface token"
)
query_engine2 = build_query_engine(falcon_llm)
result_ds_falcon = generate_responses(query_engine2, test_questions, test_answers)
result = evaluate(
    result_ds_falcon,
    metrics=metrics,
)

result
```

```python
{'faithfulness': 0.6909, 'answer_relevancy': 0.8651, 'answer_correctness': 0.5850}
```

## 对比分数

根据评估结果，在本 RAG 流水线及自有数据上，HuggingFace zephyr-7b-alpha 的 `faithfulness`、`answer_correctness` 和 `answer_relevancy` 略优于 falcon-7b-instruct。

完整 Colab notebook 见[此处](https://colab.research.google.com/drive/10dNeU56XLOGUJ9gRuBFryyRwoy70rIeS?usp=sharing)。

```python
import numpy as np
import matplotlib.pyplot as plt

def analysis(zephyr_df, falcon_df):
  sns.set_style("whitegrid")
  fig, axs = plt.subplots(1,3, figsize=(12, 5))
  for i,col in enumerate(zephyr_df.columns):
    sns.kdeplot(data=[zephyr_df[col].values,falcon_df[col].values],legend=False,ax=axs[i],fill=True)
    axs[i].set_title(f'{col} scores distribution')
    axs[i].legend(labels=["zephyr", "falcon"])
  plt.tight_layout()
  plt.show()

result_zephyr_df = result_zephyr.to_pandas()
result_falcon_df = result.to_pandas()
analysis(
    result_zephyr_df[['faithfulness', 'answer_relevancy', 'answer_correctness']],
    result_falcon_df[['faithfulness', 'answer_relevancy', 'answer_correctness']]
)
```

### 分数分布分析

<figure markdown="span">
![Compare LLMs](../../_static/imgs/compare-llm-result.png){width="800"}
<figcaption>比较 LLM</figcaption>
</figure>
