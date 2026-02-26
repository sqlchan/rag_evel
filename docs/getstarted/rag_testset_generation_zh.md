# RAG 测试集生成

本指南将帮助你使用自己的文档为 RAG 流水线生成评估用测试集。

## 快速开始

通过一个简单示例了解如何为 RAG 流水线生成测试集，然后我们会介绍测试集生成流水线的主要组件。

### 加载示例文档

本教程使用该 [仓库](https://huggingface.co/datasets/vibrantlabsai/Sample_Docs_Markdown) 中的示例文档。你可以替换为自己的文档。

```bash
git clone https://huggingface.co/datasets/vibrantlabsai/Sample_Docs_Markdown
```

### 加载文档

使用 [langchain_community](https://python.langchain.com/docs/concepts/document_loaders/) 中的 `DirectoryLoader` 从示例数据集加载文档。也可以使用 [llama_index](https://docs.llamaindex.ai/en/stable/understanding/loading/llamahub/) 的任意加载器。

```shell
pip install langchain-community
```

```python
from langchain_community.document_loaders import DirectoryLoader

path = "Sample_Docs_Markdown/"
loader = DirectoryLoader(path, glob="**/*.md")
docs = loader.load()
```

### 选择 LLM

你可以选择任意 [LLM](./../howtos/customizations/customize_models.md)。
--8<--
choose_generator_llm.md
--8<--

### 生成测试集

使用已加载的文档和 LLM 配置运行测试生成。若使用 `llama_index` 加载文档，请改用 `generate_with_llama_index_docs` 方法。

```python
from ragas.testset import TestsetGenerator

generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
dataset = generator.generate_with_langchain_docs(docs, testset_size=10)
```

### 分析测试集

生成测试集后，你可能希望查看并筛选要纳入最终测试集的查询。可将测试集导出为 pandas DataFrame 并进行各种分析。

```python
dataset.to_pandas()
```

输出
![testset](./testset_output.png)

!!! note
    生成合成测试数据可能令人困惑且困难，如需帮助我们可以协助。我们已为多种场景搭建了测试数据生成流水线。如需支持，请通过预约 [时段](https://bit.ly/3EBYq4J) 或发邮件 [founders@vibrantlabs.com](mailto:founders@vibrantlabs.com) 与我们联系。

## 深入理解

了解了如何生成测试集后，下面更详细地看看测试集生成流水线的主要组件及如何快速自定义。

核心上有 2 个主要步骤用于生成测试集：

1. **知识图谱构建**：首先用你提供的文档构建 [KnowledgeGraph][ragas.testset.graph.KnowledgeGraph]，并利用多种 [Transformations][ragas.testset.transforms.base.BaseGraphTransformation] 丰富知识图谱，以便生成测试集。更多内容见 [核心概念](../concepts/test_data_generation/rag.md#knowledge-graph-creation)。
2. **测试集生成**：使用 [KnowledgeGraph][ragas.testset.graph.KnowledgeGraph] 生成一组 [scenarios][ragas.testset.synthesizers.base.BaseScenario]，再基于这些 scenario 生成 [testset][ragas.testset.synthesizers.generate.Testset]。更多内容见 [核心概念](../concepts/test_data_generation/rag.md#scenario-generation)。

下面通过示例看这些组件如何协作生成测试集。

### 知识图谱构建

先用前面加载的文档创建 [KnowledgeGraph][ragas.testset.graph.KnowledgeGraph]。

```python
from ragas.testset.graph import KnowledgeGraph

kg = KnowledgeGraph()
```
输出
```
KnowledgeGraph(nodes: 0, relationships: 0)
```

然后将文档加入知识图谱。

```python
from ragas.testset.graph import Node, NodeType

for doc in docs:
    kg.nodes.append(
        Node(
            type=NodeType.DOCUMENT,
            properties={"page_content": doc.page_content, "document_metadata": doc.metadata}
        )
    )
```
输出
```
KnowledgeGraph(nodes: 10, relationships: 0)
```

接着使用 [Transformations][ragas.testset.transforms.base.BaseGraphTransformation] 丰富知识图谱。这里使用 [default_transforms][ragas.testset.transforms.default_transforms] 创建一组默认变换，并搭配你选择的 LLM 和嵌入模型。你也可以按需组合变换或自行实现。

```python
from ragas.testset.transforms import default_transforms, apply_transforms


# 定义你的 LLM 和嵌入模型
# 这里使用与生成测试集时相同的 LLM 和嵌入模型
transformer_llm = generator_llm
embedding_model = generator_embeddings

trans = default_transforms(documents=docs, llm=transformer_llm, embedding_model=embedding_model)
apply_transforms(kg, trans)
```

此时知识图谱已包含额外信息。你也可以保存知识图谱。

```python
kg.save("knowledge_graph.json")
loaded_kg = KnowledgeGraph.load("knowledge_graph.json")
loaded_kg
```

输出
```
KnowledgeGraph(nodes: 48, relationships: 605)
```

### 测试集生成

使用 `loaded_kg` 创建 [TestsetGenerator][ragas.testset.synthesizers.generate.TestsetGenerator]。

```python
from ragas.testset import TestsetGenerator

generator = TestsetGenerator(llm=generator_llm, embedding_model=embedding_model, knowledge_graph=loaded_kg)
```

可以定义要生成的查询分布，这里使用默认分布。

```python
from ragas.testset.synthesizers import default_query_distribution

query_distribution = default_query_distribution(generator_llm)
```

输出
```
[
    (SingleHopSpecificQuerySynthesizer(llm=llm), 0.5),
    (MultiHopAbstractQuerySynthesizer(llm=llm), 0.25),
    (MultiHopSpecificQuerySynthesizer(llm=llm), 0.25),
]
```

然后生成测试集。

```python
testset = generator.generate(testset_size=10, query_distribution=query_distribution)
testset.to_pandas()
```
输出
![testset](./testset_output.png)
