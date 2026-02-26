# 评估简单 RAG 系统

本指南旨在说明使用 `ragas` 测试和评估 RAG 系统的简单工作流。假定你对构建 RAG 系统与评估仅有基础了解。安装 `ragas` 请参考 [安装说明](./install.md)。

## 基本配置

我们将使用 `langchain_openai` 配置 LLM 和嵌入模型以构建简单 RAG。你也可以选择其他 LLM 和嵌入模型，详见 [在 LangChain 中自定义模型](https://python.langchain.com/docs/integrations/chat/)。


```python
from langchain_openai import ChatOpenAI
from ragas.embeddings import OpenAIEmbeddings
import openai

llm = ChatOpenAI(model="gpt-4o")
openai_client = openai.OpenAI()
embeddings = OpenAIEmbeddings(client=openai_client)
```

!!! note "OpenAI Embeddings API"
    `ragas.embeddings.OpenAIEmbeddings` 提供 `embed_text`（单条）和 `embed_texts`（批量），而不是像部分 LangChain 封装那样的 `embed_query`/`embed_documents`。下面示例中对文档使用 `embed_texts`，对查询使用 `embed_text`。详见 [OpenAI embeddings 实现](https://docs.ragas.io/en/stable/references/embeddings/\#ragas.embeddings.OpenAIEmbeddings)

### 构建简单 RAG 系统

要构建简单 RAG 系统，需要定义以下组件：

- 定义文档向量化方法
- 定义检索相关文档的方法
- 定义生成回答的方法

??? note "点击查看代码"

    ```python

    import numpy as np

    class RAG:
        def __init__(self, model="gpt-4o"):
            import openai
            self.llm = ChatOpenAI(model=model)
            openai_client = openai.OpenAI()
            self.embeddings = OpenAIEmbeddings(client=openai_client)
            self.doc_embeddings = None
            self.docs = None

        def load_documents(self, documents):
            """加载文档并计算其嵌入。"""
            self.docs = documents
            self.doc_embeddings = self.embeddings.embed_texts(documents)

        def get_most_relevant_docs(self, query):
            """根据查询找到最相关的文档。"""
            if not self.docs or not self.doc_embeddings:
                raise ValueError("Documents and their embeddings are not loaded.")
            
            query_embedding = self.embeddings.embed_text(query)
            similarities = [
                np.dot(query_embedding, doc_emb)
                / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb))
                for doc_emb in self.doc_embeddings
            ]
            most_relevant_doc_index = np.argmax(similarities)
            return [self.docs[most_relevant_doc_index]]

        def generate_answer(self, query, relevant_doc):
            """根据最相关文档为给定查询生成回答。"""
            prompt = f"question: {query}\n\nDocuments: {relevant_doc}"
            messages = [
                ("system", "You are a helpful assistant that answers questions based on given documents only."),
                ("human", prompt),
            ]
            ai_msg = self.llm.invoke(messages)
            return ai_msg.content
    ```

### 加载文档

下面加载一些文档并测试 RAG 系统。

```python
sample_docs = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine."
]
```

```python
# 初始化 RAG 实例
rag = RAG()

# 加载文档
rag.load_documents(sample_docs)

# 查询并检索最相关文档
query = "Who introduced the theory of relativity?"
relevant_doc = rag.get_most_relevant_docs(query)

# 生成回答
answer = rag.generate_answer(query, relevant_doc)

print(f"Query: {query}")
print(f"Relevant Document: {relevant_doc}")
print(f"Answer: {answer}")
```


输出：
```
Query: Who introduced the theory of relativity?
Relevant Document: ['Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.']
Answer: Albert Einstein introduced the theory of relativity.
```

## 收集评估数据

要收集评估数据，首先需要一组针对 RAG 的查询。我们让这些查询经过 RAG 系统，并收集每条查询的 `response`、`retrieved_contexts`。你也可以 optionally 为每条查询准备参考答案，用于评估系统表现。



```python


sample_queries = [
    "Who introduced the theory of relativity?",
    "Who was the first computer programmer?",
    "What did Isaac Newton contribute to science?",
    "Who won two Nobel Prizes for research on radioactivity?",
    "What is the theory of evolution by natural selection?"
]

expected_responses = [
    "Albert Einstein proposed the theory of relativity, which transformed our understanding of time, space, and gravity.",
    "Ada Lovelace is regarded as the first computer programmer for her work on Charles Babbage's early mechanical computer, the Analytical Engine.",
    "Isaac Newton formulated the laws of motion and universal gravitation, laying the foundation for classical mechanics.",
    "Marie Curie was a physicist and chemist who conducted pioneering research on radioactivity and won two Nobel Prizes.",
    "Charles Darwin introduced the theory of evolution by natural selection in his book 'On the Origin of Species'."
]
```

```python
dataset = []

for query,reference in zip(sample_queries,expected_responses):
    
    relevant_docs = rag.get_most_relevant_docs(query)
    response = rag.generate_answer(query, relevant_docs)
    dataset.append(
        {
            "user_input":query,
            "retrieved_contexts":relevant_docs,
            "response":response,
            "reference":reference
        }
    )
```

将数据集加载到 `EvaluationDataset` 对象中。

```python
from ragas import EvaluationDataset
evaluation_dataset = EvaluationDataset.from_list(dataset)
```

## 评估

评估数据已准备好。现在可以使用一组常用 RAG 评估指标在收集到的数据集上评估 RAG 系统。评估时可选用任意模型作为 [评估用 LLM](./../howtos/customizations/customize_models.md)。

```python
from ragas import evaluate
from ragas.llms import LangchainLLMWrapper


evaluator_llm = LangchainLLMWrapper(llm)
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness

result = evaluate(dataset=evaluation_dataset,metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],llm=evaluator_llm)
result
```

输出
```
{'context_recall': 1.0000, 'faithfulness': 0.8571, 'factual_correctness': 0.7280}
```

### 需要借助评估改进你的 AI 应用？

过去两年里，我们通过评估帮助了许多 AI 应用改进。

我们正在把这些经验沉淀成产品，用评估循环替代“感觉好不好”的检查，让你更专注于把 AI 应用做好。

若你希望借助评估改进和扩展 AI 应用：

🔗 预约 [时段](https://bit.ly/3EBYq4J) 或发邮件：[founders@vibrantlabs.com](mailto:founders@vibrantlabs.com)。

![](../_static/ragas_app.gif)


## 下一步

- [为 RAG 评估生成测试数据](rag_testset_generation.md)
