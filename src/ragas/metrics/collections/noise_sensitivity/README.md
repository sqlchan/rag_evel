# Noise Sensitivity（噪声敏感度）

## 功能概述

衡量系统在**相关/无关检索文档**下的错误率：当使用相关文档或无关文档时，模型是否更容易产生与参考答案不一致的陈述。分数**越低越好**。

## 模式

- **relevant**：在「与参考答案相关的检索」下，回答中错误陈述的比例（本应正确却错了）
- **irrelevant**：在「与参考答案无关的检索」下，回答却错误地依赖了这些无关内容的比例

## 核心逻辑

1. 将 reference 与 response 分别分解为陈述
2. 对每个 retrieved context：用 NLI 判断「参考陈述是否被该 context 支持」「回答陈述是否被该 context 支持」
3. 用 NLI 判断「回答陈述是否被 reference 支持」，得到 ground_truth2answer
4. 根据 relevant/irrelevant 模式，从上述矩阵中取相应子集，计算「错误」比例（如 relevant_faithful & incorrect 的均值）

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `NoiseSensitivity`：陈述分解、多 context NLI、矩阵构建、score 计算 |
| `util.py` | 陈述生成与 NLI 的输入/输出及 Prompt（与 faithfulness 类似） |

## 依赖

- **LLM**：陈述分解 + NLI

## 使用示例

```python
metric = NoiseSensitivity(llm=llm, mode="relevant")
result = await metric.ascore(
    user_input="LIC 以什么闻名？",
    response="LIC 是印度最大保险公司……",
    reference="LIC 以管理投资闻名……",
    retrieved_contexts=["LIC 成立于 1956 年……", ...],
)
```
