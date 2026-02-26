## 语义相似度

**语义相似度**（Semantic Similarity）衡量生成回答与参考答案（标准答案）在语义上的接近程度。分数范围为 0 到 1，越高表示生成答案与标准答案越一致。 

该指标使用嵌入与余弦相似度衡量两句回答的语义相似程度，可为生成回答的质量提供有用信息。

### 示例

（代码保持英文。）

```python
from openai import AsyncOpenAI
from ragas.embeddings import OpenAIEmbeddings
from ragas.metrics.collections import SemanticSimilarity

# Setup embeddings
client = AsyncOpenAI()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=client)

# Create metric
scorer = SemanticSimilarity(embeddings=embeddings)

# Evaluate
result = await scorer.ascore(
    reference="The Eiffel Tower is located in Paris. It has a height of 1000ft.",
    response="The Eiffel Tower is located in Paris."
)
print(f"Semantic Similarity Score: {result.value}")
```

输出：

```
Semantic Similarity Score: 0.8151
```

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

### 计算方式

!!! example
    **标准答案**：阿尔伯特·爱因斯坦的相对论彻底改变了我们对宇宙的理解。

    **高相似度回答**：爱因斯坦的开创性相对论改变了我们对宇宙的认识。

    **低相似度回答**：艾萨克·牛顿的运动定律对经典物理学影响深远。

高相似度回答的计算步骤：  
- **步骤 1**：用指定嵌入模型将标准答案向量化。  
- **步骤 2**：用同一嵌入模型将生成回答向量化。  
- **步骤 3**：计算两个向量的余弦相似度。  
- **步骤 4**：该余弦相似度（0–1）即为最终分数。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。
