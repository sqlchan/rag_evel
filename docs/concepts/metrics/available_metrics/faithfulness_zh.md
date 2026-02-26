## 忠实度

**忠实度**（Faithfulness）衡量 `response` 与 `retrieved context` 在事实层面的一致性。分数范围为 0 到 1，越高表示一致性越好。

若回答中的**所有**陈述都能由检索到的上下文支持，则视为**忠实**。

计算步骤：
1. 识别回答中的所有陈述。
2. 逐条检查该陈述是否能从检索上下文中推断得出。
3. 用下式计算忠实度分数：

$$
\text{Faithfulness Score} = \frac{\text{回答中被检索上下文支持的陈述数}}{\text{回答中陈述总数}}
$$


### 示例

（代码保持英文。）

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

# Setup LLM
client = AsyncOpenAI()
llm = llm_factory("gpt-4o-mini", client=client)

# Create metric
scorer = Faithfulness(llm=llm)

# Evaluate
result = await scorer.ascore(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967",
    retrieved_contexts=[
        "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
    ]
)
print(f"Faithfulness Score: {result.value}")
```

输出：

```
Faithfulness Score: 1.0
```

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

### 计算方式

!!! example
    **问题**：爱因斯坦在哪里、何时出生？

    **上下文**：Albert Einstein (born 14 March 1879) was a German-born theoretical physicist...

    **高忠实度回答**：爱因斯坦 1879 年 3 月 14 日出生于德国。

    **低忠实度回答**：爱因斯坦 1879 年 3 月 20 日出生于德国。

以低忠实度回答为例：  
- **步骤 1**：将生成答案拆成独立陈述。  
- **步骤 2**：对每条陈述判断是否能从给定上下文推断。  
- **步骤 3**：用上述公式计算忠实度。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。

（Legacy 示例与 FaithfulnesswithHHEM 用法保留英文，与原文一致。）
