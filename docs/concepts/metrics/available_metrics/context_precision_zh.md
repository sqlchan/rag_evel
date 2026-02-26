# 上下文精确率

上下文精确率（Context Precision）评估检索器在给定查询下，将相关块排在无关块前面的能力；具体是衡量检索上下文中相关块在排序中靠前的程度。

计算方式为上下文中各块的 precision@k 的均值。Precision@k 为排名 k 处相关块数量与排名 k 处总块数之比。

$$
\text{Context Precision@K} = \frac{\sum_{k=1}^{K} \left( \text{Precision@k} \times v_k \right)}{\text{前 } K \text{ 个结果中的相关项总数}}
$$

$$
\text{Precision@k} = {\text{true positives@k} \over  (\text{true positives@k} + \text{false positives@k})}
$$

其中 $K$ 为 `retrieved_contexts` 中的块总数，$v_k \in 0, 1$ 为排名 $k$ 处的相关性指示。

## 示例

### Context Precision

`ContextPrecision` 通过将每个检索上下文与参考答案对比，评估检索上下文是否有助于回答问题。在有参考答案时使用。

（代码示例与原文一致，见 [context_precision.md](context_precision.md)。）

### Context Utilization

`ContextUtilization` 通过将每个上下文与生成回答对比，评估检索上下文是否有用。在没有参考答案但有生成回答时使用。

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

## 非基于 LLM 的上下文精确率

使用非 LLM 方法（如 [Levenshtein 距离](https://en.wikipedia.org/wiki/Levenshtein_distance)）判断检索上下文是否相关。需安装 rapidfuzz：`pip install rapidfuzz`。

## 基于 ID 的上下文精确率

IDBasedContextPrecision 通过比较检索上下文 ID 与参考上下文 ID 直接衡量精确率，适用于有文档唯一 ID 且不想比较正文内容的场景。公式：

$$ \text{ID-Based Context Precision} = \frac{\text{出现在参考上下文 ID 中的检索上下文 ID 数}}{\text{检索上下文 ID 总数}} $$ 

详细示例与 Legacy API 见 [context_precision.md](context_precision.md)。