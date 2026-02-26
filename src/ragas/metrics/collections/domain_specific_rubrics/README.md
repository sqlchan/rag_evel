# Domain Specific Rubrics（领域定制 rubric）

## 功能概述

用**自定义 1–5 分 rubric** 对回答做整体打分，支持**无参考**与**有参考**两种模式。Rubric 描述各分数档位的含义，由 LLM 据此给出分数和反馈。

## 核心逻辑

1. 若未传入 `rubrics`，则使用默认的 `DEFAULT_REFERENCE_FREE_RUBRICS` 或 `DEFAULT_WITH_REFERENCE_RUBRICS`
2. 将 rubric 文本拼进 scoring prompt 的 instruction
3. 输入：user_input、response、可选 reference / retrieved_contexts / reference_contexts
4. LLM 输出：score（1–5）与 feedback；`allowed_values=(1.0, 5.0)`

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `DomainSpecificRubrics`、`RubricsScoreWithoutReference`、`RubricsScoreWithReference` |
| `util.py` | `RubricScoreInput/Output`、`RubricScorePrompt`、`format_rubrics`、默认 rubric 字典 |

## 依赖

- **LLM**：按 rubric 打分并生成反馈

## 使用示例

```python
metric = DomainSpecificRubrics(llm=llm, with_reference=False)
result = await metric.ascore(
    user_input="法国首都是哪？",
    response="法国首都是巴黎。",
)
# result.value 1–5, result.reason 为反馈文本
```
