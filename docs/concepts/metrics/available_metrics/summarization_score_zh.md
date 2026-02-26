# 任务指标

## 摘要分数（Summarization Score）

**Summarization Score** 衡量摘要（`response`）对 `reference_contexts` 中重要信息的保留程度。思路是：好的摘要应包含上下文中所有重要信息。 

步骤：先从上下文中抽取重要关键短语，用其生成一组问题，这些问题的答案在上下文中恒为“是”(1)。再对摘要问同样的问题，摘要分数 = 正确回答数 / 总问题数。

$$
\text{QA score} = \frac{|\text{正确回答的问题数}|}{|\text{总问题数}|}
$$

可选地引入简洁性惩罚：较长摘要会降低简洁性分数。若启用，最终分数为摘要分数与简洁性分数的加权平均（默认权重系数 `coeff=0.5`）。

$$
\text{conciseness score} = 1 - \frac{\min(\text{摘要长度}, \text{上下文长度})}{\text{上下文长度} + \text{1e-10}}
$$

详见 [summarization_score.md](summarization_score.md)。

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。
