# CHRF Score（字符级 F 分数）

## 功能概述

**基于字符 n-gram 的 F 分数**，常用于机器翻译质量评估。与 BLEU 不同，CHRF 在字符级别计算，对形态变化和不同语言更稳健。使用 sacrebleu 的 `corpus_chrf`，结果除以 100 归一化到 0.0–1.0。

## 核心逻辑

1. 将 reference 与 response 转为 sacrebleu 所需格式（references 为 list of list of str，hypotheses 为 list of str）
2. 调用 `corpus_chrf(hypotheses, references, **kwargs).score / 100`
3. 空串或非字符串输入返回 0.0 并带 reason

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `CHRFScore`：输入校验、调用 sacrebleu、归一化 |

## 依赖

- **sacrebleu**：需安装 `pip install sacrebleu`
- 无 LLM

## 使用示例

```python
metric = CHRFScore()
result = await metric.ascore(
    reference="法国首都是巴黎。",
    response="巴黎是法国首都。",
)
```
