## 答案正确性

答案正确性（Answer Correctness）的评估是衡量生成答案与标准答案相比的准确程度。该评估依赖 `ground truth` 与 `answer`，分数范围为 0 到 1。分数越高表示生成答案与标准答案越一致，正确性越好。

答案正确性包含两个关键方面：生成答案与标准答案的语义相似度，以及事实相似度。这两方面通过加权方式组合成答案正确性分数。用户也可选择使用「阈值」将结果分数二值化。

!!! note "嵌入要求"
    AnswerCorrectness 需要嵌入以计算语义相似度。使用 `evaluate()` 且未显式提供嵌入时，Ragas 会自动将嵌入提供方与 LLM 提供方匹配。例如若使用 Gemini 作为 LLM，将自动使用 Google 嵌入（无需 OpenAI API 密钥）。你也可以显式提供嵌入以完全控制。


!!! example
    **标准答案**：爱因斯坦 1879 年出生于德国。

    **高答案正确性**：爱因斯坦于 1879 年在德国出生。

    **低答案正确性**：爱因斯坦 1879 年出生于西班牙。


### 示例

（代码块保持英文，与原文一致。）

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory
from ragas.metrics.collections import AnswerCorrectness

# Setup LLM and embeddings
client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)
embeddings = embedding_factory("openai", model="text-embedding-3-small", client=client)

# Create metric
scorer = AnswerCorrectness(llm=llm, embeddings=embeddings)

# Evaluate
result = await scorer.ascore(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967",
    reference="The first superbowl was held on January 15, 1967"
)
print(f"Answer Correctness Score: {result.value}")
```

输出：

```
Answer Correctness Score: 0.95
```

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`：
    
    ```python
    result = scorer.score(
        user_input="When was the first super bowl?",
        response="The first superbowl was held on Jan 15, 1967",
        reference="The first superbowl was held on January 15, 1967"
    )
    ```

### 计算方式

以低答案正确性的回答为例。分数由事实正确性与给定答案和标准答案的语义相似度之和计算。

事实正确性量化生成答案与标准答案的事实重叠，使用以下概念：
- TP（True Positive）：同时出现在标准答案与生成答案中的事实或陈述。
- FP（False Positive）：出现在生成答案但不在标准答案中的事实或陈述。
- FN（False Negative）：出现在标准答案但不在生成答案中的事实或陈述。

在第二个示例中：
- TP: `[Einstein was born in 1879]`
- FP: `[Einstein was born in Spain]`
- FN: `[Einstein was born in Germany]`

然后使用 F1 分数公式，根据上述列表中的陈述数量量化正确性：

$$
\text{F1 Score} = {|\text{TP} \over {(|\text{TP}| + 0.5 \times (|\text{FP}| + |\text{FN}|))}}
$$

接着计算生成答案与标准答案的语义相似度。更多说明见[此处](./semantic_similarity_zh.md)。

得到语义相似度后，对语义相似度与上述事实相似度取加权平均得到最终分数。可通过修改 `weights` 参数调整权重。

## 旧版指标 API

以下示例使用旧版指标 API。新项目建议使用上文所示的集合类 API。

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。

（旧版 Dataset 示例保留英文，与原文一致。）
