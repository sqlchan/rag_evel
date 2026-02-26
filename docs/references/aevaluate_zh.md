# 异步评估

## aevaluate()

::: ragas.evaluation.aevaluate

## 异步用法

Ragas 同时提供同步与异步评估 API，以适应不同场景：

### 使用 aevaluate()（推荐用于生产环境）

在生产环境的异步应用中，使用 `aevaluate()` 可避免事件循环冲突：

```python
import asyncio
from ragas import aevaluate

async def evaluate_app():
    result = await aevaluate(dataset, metrics)
    return result

# 在你的异步应用中
result = await evaluate_app()
```

### 使用 evaluate() 并控制异步行为

为兼容旧用法及 Jupyter notebook，`evaluate()` 提供对 `nest_asyncio` 的可选控制：

```python
# 默认行为（兼容 Jupyter）
result = evaluate(dataset, metrics)  # allow_nest_asyncio=True

# 生产环境更安全（避免修补事件循环）
result = evaluate(dataset, metrics, allow_nest_asyncio=False)
```

### 从 nest_asyncio 问题迁移

若在生产环境中遇到 `nest_asyncio` 相关问题：

**之前（可能有问题）：**
```python
# 可能导致事件循环冲突
result = evaluate(dataset, metrics)
```

**之后（修复）：**
```python
# 方式 1：使用异步 API
result = await aevaluate(dataset, metrics)

# 方式 2：禁用 nest_asyncio
result = evaluate(dataset, metrics, allow_nest_asyncio=False)
```
