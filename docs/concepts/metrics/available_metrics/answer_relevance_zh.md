## 回答相关性

**回答相关性**（Answer Relevancy）衡量回答与用户输入的相关程度，分数范围为 0 到 1，越高表示与用户输入越一致。若回答直接、恰当地回应原始问题，则视为相关；该指标不评估事实准确性，会惩罚不完整或含多余细节的回答。

使用 `user_input` 和 `response` 计算：  

1. 根据回答生成一组人工问题（默认 3 个）；
2. 计算用户输入嵌入与每个生成问题嵌入的余弦相似度；
3. 取这些余弦相似度的平均作为**回答相关性**。

**注意**：分数通常落在 0 到 1 之间，但因余弦相似度范围为 -1 到 1，不保证一定在此范围。

### 示例

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from ragas.metrics.collections import AnswerRelevancy

client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)
embeddings = embedding_factory("openai", model="text-embedding-3-small", client=client)

scorer = AnswerRelevancy(llm=llm, embeddings=embeddings)

result = await scorer.ascore(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967"
)
print(f"Answer Relevancy Score: {result.value}")
```

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

### 计算思路

从生成答案用 LLM 反推 n 个问题变体，再计算这些生成问题与实际问题的平均余弦相似度。若回答正确对应问题，则仅从回答重建原问题的概率较高。 

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。