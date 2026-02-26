# Quoted Spans Alignment（引用片段对齐）

## 功能概述

**规则指标**：评估回答中**引号内片段**有多少能在 `retrieved_contexts` 中找到（逐字或经轻量归一化后匹配）。用于衡量引用是否真实来源于给定文档。

## 核心逻辑

1. 从 `response` 中提取引号内片段（`extract_quoted_spans`），可配置最小词数 `min_span_words`
2. 对每个片段，在 `retrieved_contexts` 中做子串匹配；可选 `casefold` 忽略大小写
3. 分数 = 匹配到的片段数 / 总片段数；若无引号片段则返回 1.0（视为无引用可验证）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `QuotedSpansAlignment`：抽引用、匹配、算比例 |
| `util.py` | `extract_quoted_spans`、`count_matched_spans`（含归一化与匹配逻辑） |

## 依赖

- 无 LLM，纯字符串与正则处理

## 使用示例

```python
metric = QuotedSpansAlignment(casefold=True, min_span_words=3)
result = await metric.ascore(
    response='研究称"机器学习模型提升了准确率"。',
    retrieved_contexts=["机器学习模型将准确率提高了 15%。"],
)
```
