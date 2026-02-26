# 上下文召回率

上下文召回率（Context Recall）衡量有多少相关文档（或信息片段）被成功检索到，关注不遗漏重要结果。召回越高，被漏掉的相关文档越少。

因为关注“不遗漏”，计算上下文召回率始终需要参考答案作为对比。基于 LLM 的 Context Recall 用 `reference` 作为 `reference_contexts` 的代理，便于使用（标注参考上下文通常很耗时）。从 `reference` 估计召回时，会将 reference 拆成陈述，并逐条判断是否可归因于检索上下文。理想情况下，参考答案中的所有陈述都应能归因于检索上下文。

公式：

$$
\text{Context Recall} = \frac{\text{被检索上下文支持的 reference 中的陈述数}}{\text{reference 中陈述总数}}
$$

## 示例

（代码与原文一致，见 [context_recall.md](context_recall.md)。）

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

## 非基于 LLM 的上下文召回率

`NonLLMContextRecall` 使用 `retrieved_contexts` 和 `reference_contexts` 计算，分数在 0 到 1 之间，越高越好。通过非 LLM 的字符串比较判断检索上下文是否相关。 

## 基于 ID 的上下文召回率

IDBasedContextRecall 通过比较检索上下文 ID 与参考上下文 ID 直接衡量召回，适用于有文档唯一 ID 的场景。

$$ \text{ID-Based Context Recall} = \frac{\text{出现在检索上下文 ID 中的参考上下文 ID 数}}{\text{参考上下文 ID 总数}} $$

详细示例与 Legacy API 见 [context_recall.md](context_recall.md)。