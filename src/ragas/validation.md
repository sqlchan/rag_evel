# ragas/validation.py 功能说明

## 概述
评估前的数据集校验：列名重映射、支持的单轮/多轮类型判断、必选列与指标类型匹配检查。

## remap_column_names
- **column_map**: 新列名 -> 旧列名（或反之），对 HuggingFace Dataset 做 rename_columns(inverse_map)，使评估代码看到统一列名。

## get_supported_metric_type
- 根据 **ds.get_sample_type()** 返回 **MetricType.SINGLE_TURN** 或 **MetricType.MULTI_TURN** 的 name；其他类型抛 ValueError。

## validate_required_columns
- 取 metric_type（单轮/多轮），对每个 metric 取 required_columns[metric_type]，与 **ds.features()** 比较；缺少列时抛出 ValueError，并列出缺失列与 metric 名。

## validate_supported_metrics
- 对每个 metric：若为 SingleTurnSample 则要求 SingleTurnMetric，若为 MultiTurnSample 则要求 MultiTurnMetric；否则抛出「该指标不支持当前样本类型」的 ValueError。
