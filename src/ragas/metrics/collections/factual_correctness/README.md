# Factual Correctness（事实正确性）

## 功能概述

评估**回答与参考文本在事实层面的一致性**。通过「陈述分解 + NLI 验证」双向检查：回答中的声称是否被参考支持、参考中的声称是否被回答覆盖。

## 核心逻辑

1. **分解**：用 LLM 将 response 与 reference 分别分解为 claims（可配置 atomicity / coverage）
2. **验证**：response 的 claims 对 reference 做 NLI → 得到 TP/FP；reference 的 claims 对 response 做 NLI → 得到 FN（仅 recall/f1 模式）
3. **得分**：按 mode 计算 precision、recall 或 F-β

## 模式与参数

- **mode**：`"precision"`（仅 response→reference）、`"recall"`、`"f1"`
- **beta**：F-β 的 β
- **atomicity** / **coverage**：分解粒度与覆盖度（low/high）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `FactualCorrectness`：分解、双向验证、TP/FP/FN、precision/recall/f1 |
| `util.py` | 陈述分解与 NLI 的模型与多组 atomicity/coverage 示例 |

## 依赖

- **LLM**：claim 分解 + NLI

## 使用示例

```python
metric = FactualCorrectness(llm=llm, mode="f1", beta=1.0)
result = await metric.ascore(
    response="爱因斯坦 1879 年生于德国。",
    reference="阿尔伯特·爱因斯坦 1879 年 3 月 14 日生于德国乌尔姆。",
)
```
