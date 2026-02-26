# 基于量表的评估

基于量表的评估指标允许用自定义评分准则评估 LLM 回答。Ragas 提供两类量表指标：

1. **DomainSpecificRubrics**：对数据集中所有样本使用同一量表（在初始化时设定）  
2. **InstanceSpecificRubrics**：每个样本可有自己的量表（在每次评估时传入）  

量表由各分数（通常 1–5）的描述组成，LLM 根据描述对回答打分。

## 领域级量表（Domain-Specific Rubrics）

当希望对所有样本使用同一套评估准则时使用 `DomainSpecificRubrics`。可无参考（默认）或有参考评估；支持自定义量表；支持带 `retrieved_contexts` 的评估。便捷类：`RubricsScoreWithoutReference`、`RubricsScoreWithReference`。

## 默认量表

**无参考**：1=完全错误/未回应；2=部分正确但重大错误或遗漏；3=大致正确但不够清晰或完整；4=正确清晰仅小遗漏；5=完全正确清晰且完整。  
**有参考**：1=完全错误或与参考不符；2=部分匹配但有重大错误或遗漏；3=整体符合参考但不够详细或清晰；4=大致准确、与参考接近仅小问题；5=完全准确、与参考完全一致、清晰详细。

## 实例级量表（Instance-Specific Rubrics）

当不同样本需要不同评估准则时使用 `InstanceSpecificRubrics`，例如不同问题对应不同标准，或按任务定制评分。每次调用 `ascore` 时可传入该样本的 `rubrics`。详见 [rubrics_based.md](rubrics_based.md)。

## 旧版 API

!!! warning "已弃用"
    旧版 API 已弃用。请使用 `ragas.metrics.collections.DomainSpecificRubrics` 或 `ragas.metrics.collections.InstanceSpecificRubrics`。
