# 通用指标

通用评估指标用于评估任意给定任务。

## 方面批评（Aspect Critic）

`AspectCritic` 可根据预定义方面以自由形式自然语言评估回答，输出为二元（是否符合该方面）。详见 [aspect_critic_zh.md](aspect_critic_zh.md)。

## 简单准则评分（Simple Criteria Scoring）

根据预定义准则对回答打分，输出可为指定范围内的整数或自定义类别。可用 `DiscreteMetric` 实现自定义分数范围与准则。示例：整数范围评分、自定义范围评分、基于相似度的评分。详见 [general_purpose.md](general_purpose.md)。

## 基于量表的准则评分（Rubrics based criteria scoring）

基于用户定义量表的评估，每个量表通常为 1–5 分的描述，LLM 按描述对回答打分。定义量表时术语需与 `SingleTurnSample` 或 `MultiTurnSample` 的 schema 一致（如使用 reference 则量表也用 reference）。详见 [general_purpose.md](general_purpose.md) 与 [rubrics_based_zh.md](rubrics_based_zh.md)。

## 实例级量表评分（Instance specific rubrics scoring）

对数据集中每条样本使用**不同**量表进行评估（每条样本可带自己的 rubric）。与“全数据集共用同一量表”的 Rubric Based 不同。示例与用法见 [general_purpose.md](general_purpose.md)。
