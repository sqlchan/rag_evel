# Nvidia 指标

## 答案准确率（Answer Accuracy）

**Answer Accuracy** 衡量模型回答与给定问题的参考答案的一致程度。通过两个不同的「LLM-as-a-Judge」提示各自返回 0/2/4 的评分，再映射到 [0,1] 并取两次评分的平均。分数越高表示回答与参考越一致。  
- 0：回答不准确或未回答与参考相同的问题。  
- 2：部分一致。  
- 4：完全一致。   

示例与计算步骤见 [nvidia_metrics.md](nvidia_metrics.md)。与 Answer Correctness、Rubric Score 的对比亦见该文档。

## 上下文相关性（Context Relevance）

**Context Relevance** 评估 `retrieved_contexts` 与 `user_input` 的相关程度。通过两次独立的 LLM 评判，每次对相关性打 0/1/2 分，再归一化到 [0,1] 并取平均。  
- 0：完全不相关；1：部分相关；2：完全相关。  

与 Context Precision、Context Recall、Rubric Score 的对比见 [nvidia_metrics.md](nvidia_metrics.md)。

## 回答 grounded 程度（Response Groundedness）

**Response Groundedness** 衡量回答被检索上下文支持（“grounded”）的程度，即回答中的每条陈述是否能在上下文中找到（全部或部分）。  
- 0：完全不 grounded；1：部分；2：完全 grounded。  

与 Faithfulness、Rubric Score 的对比见 [nvidia_metrics.md](nvidia_metrics.md)。

!!! note "同步用法"
    各指标均支持 `.score()` 同步用法。
