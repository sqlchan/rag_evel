# ragas/losses.py 功能说明

## 概述
优化器用的损失抽象与两种实现：MSE 与二分类指标（accuracy/F1）损失；支持 Pydantic 校验（__get_pydantic_core_schema__）。

## Loss（抽象基类）
- **__call__(predicted, actual)**: 返回 float，子类实现。
- **__get_pydantic_core_schema__**: 使 Pydantic 能校验 Loss 子类实例。

## MSELoss
- **reduction**: "mean" 或 "sum"。
- **__call__**: 对 (predicted - actual)^2 做 mean 或 sum。

## BinaryMetricLoss
- **metric**: "accuracy" 或 "f1_score"。
- **__call__**: 校验长度一致后，按 metric 调用 _accuracy 或 _f1_score。
- **_accuracy**: 正确数/总数。
- **_f1_score**: 按 TP/FP/FN 算 precision、recall，再 2*P*R/(P+R)，边界为 0。
