## 事实正确性

`FactualCorrectness` 比较并评估生成 `response` 与 `reference` 在事实上的准确程度，分数范围为 0 到 1，越高表示与 reference 越一致。度量方式为：先用 LLM 将 response 和 reference 拆成陈述，再通过自然语言推理得到事实重叠，并用精确率、召回率和 F1 量化（可通过 `mode` 参数控制）。

### 示例

（代码与原文一致，见 [factual_correctness.md](factual_correctness.md)。）

默认 `mode` 为 `f1`，可设为 `precision` 或 `recall`。还可通过 `atomicity` 和 `coverage` 控制陈述拆分的粒度。

!!! note "同步用法"
    若偏好同步代码，可使用 `.score()` 替代 `.ascore()`。

### 计算方式

TP/FP/FN 定义：  
- TP：response 中且出现在 reference 中的陈述数  
- FP：response 中有但不在 reference 中的陈述数  
- FN：reference 中有但不在 response 中的陈述数  

再用精确率、召回率、F1 公式计算。

### 控制陈述数量

**Atomicity**：句子被拆成多细的陈述（高 atomicity = 更细、更多陈述；低 = 更少、更整句）。  
**Coverage**：陈述对原句信息的覆盖程度（高 = 保留所有细节；低 = 只保留要点）。  

组合使用可满足不同粒度的评估需求。

## 旧版指标 API

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，在 1.0 版本移除。请迁移到上文所示的集合类 API。
