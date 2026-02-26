# DataCompy Score（表格数据对比）

## 功能概述

比较**两段 CSV 字符串**（reference 与 response），按行或按列计算匹配的 precision / recall / f1。适用于 SQL 生成、表格生成等任务的结果评估。

## 核心逻辑

1. 用 pandas 将 reference 与 response 解析为 DataFrame；解析失败返回 NaN
2. 用 datacompy 的 `Compare(reference_df, response_df, on_index=True)` 比较
3. **按行**：matching_rows / reference 行数 = recall，matching_rows / response 行数 = precision
4. **按列**：按 column_stats 中 unequal_cnt==0 的列数算 recall/precision
5. 根据 `metric` 参数返回 precision、recall 或 f1

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `DataCompyScore`：CSV 解析、Compare、行列统计、precision/recall/f1 |

## 依赖

- **pandas**、**datacompy**（含 `datacompy.core.Compare` 或旧版 `datacompy.Compare`）
- 无 LLM

## 使用示例

```python
metric = DataCompyScore(mode="rows", metric="f1")
result = await metric.ascore(
    reference="id,name\n1,Alice\n2,Bob",
    response="id,name\n1,Alice\n2,Bob\n3,Charlie",
)
```
