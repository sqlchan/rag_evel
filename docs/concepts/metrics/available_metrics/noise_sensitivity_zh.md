# 噪声敏感度

`NoiseSensitivity` 衡量系统在使用相关或无关检索文档时，因给出错误回答而犯错的频率。分数范围为 0 到 1，**越低**表示表现越好。计算使用 `user_input`、`reference`、`response` 和 `retrieved_contexts`。

为估计噪声敏感度，会检查生成回答中的每条陈述：根据标准答案判断是否正确，以及是否可归因于相关（或无关）检索上下文。理想情况下，回答中的所有陈述都应由相关检索上下文支持。 

$$
\text{noise sensitivity (relevant)} = {|\text{回答中错误陈述总数}| \over |\text{回答中陈述总数}|}
$$

### 示例

（代码与原文一致，见 [noise_sensitivity.md](noise_sensitivity.md)。）

计算无关上下文的噪声敏感度时，可将 `mode` 设为 `irrelevant`。

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

## 计算方式

步骤概述：识别可从标准答案推断的相关上下文；检查回答中的陈述是否能从相关上下文推断；找出回答中不被标准答案支持的错误陈述；用上述公式计算噪声敏感度。

致谢：噪声敏感度源自 [RAGChecker](https://github.com/amazon-science/RAGChecker/tree/main/ragchecker)。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。
