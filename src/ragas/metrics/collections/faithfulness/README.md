# Faithfulness（忠实度）

## 功能概述

评估**回答是否忠实于检索上下文**：回答中的陈述是否都能由给定 context 支撑（无幻觉、无脱离上下文）。

## 核心逻辑

1. **陈述生成**：用 LLM 将回答拆成原子陈述（与 Answer Correctness 同款 StatementGenerator）
2. **NLI 判定**：对每条陈述，用 LLM 判断是否能由「合并后的 retrieved_contexts」推断（类似自然语言推理）
3. **分数**：忠实陈述数 / 总陈述数；若无陈述则返回 NaN

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `Faithfulness`：陈述生成、对 context 做 NLI、计算比例 |
| `util.py` | 陈述生成与 NLI 的输入/输出模型及 Prompt 示例 |

## 依赖

- **LLM**：陈述生成 + NLI 判定

## 使用示例

```python
metric = Faithfulness(llm=llm)
result = await metric.ascore(
    user_input="爱因斯坦在哪出生？",
    response="爱因斯坦于 1879 年 3 月 14 日在德国出生。",
    retrieved_contexts=["阿尔伯特·爱因斯坦在德国出生……"],
)
```
