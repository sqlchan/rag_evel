# Summary Score（摘要得分）

## 功能概述

评估**摘要**是否抓住原文要点：从原文抽关键短语 → 生成是非题 → 看摘要能否正确回答这些问题；并可叠加**简洁度惩罚**（摘要过长会降分）。

## 核心逻辑

1. **关键短语**：用 LLM 从合并后的 `reference_contexts` 中抽取 keyphrases
2. **生成问题**：基于 keyphrases 和原文生成若干是非题
3. **生成答案**：用 LLM 根据摘要对每题给出答案（如 1/0 表示是/否）
4. **QA 分数**：正确答案数 / 总题数
5. **可选简洁度**：conciseness = 1 - min(len(summary), len(text)) / len(text)；最终 = qa_score * (1 - coeff) + conciseness * coeff

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `SummaryScore`：关键短语、问题生成、答案生成、QA 与简洁度合并 |
| `util.py` | 各步的输入/输出模型与 Prompt（ExtractKeyphrases、GenerateQuestions、GenerateAnswers） |

## 依赖

- **LLM**：关键短语、问题、答案三步

## 使用示例

```python
metric = SummaryScore(llm=llm, length_penalty=True, coeff=0.5)
result = await metric.ascore(
    reference_contexts=["苹果公司是一家科技公司……"],
    response="苹果是由乔布斯创立的科技公司。",
)
```
