# SQL Semantic Equivalence（SQL 语义等价）

## 功能概述

评估**生成的 SQL** 与**参考 SQL** 在语义上是否等价（在同一数据库上执行结果是否一致）。不要求句法相同，由 LLM 结合 schema 判断。

## 核心逻辑

1. 可选将 `reference_contexts` 拼成 database_schema 描述
2. 用 LLM 输入：reference SQL、response SQL、schema；输出是否 equivalent 及简要解释
3. 分数：equivalent 为 1.0，否则 0.0；reason 中带解释

## 文件说明

| 文件 | 作用 |
|------|------|
| `metric.py` | `SQLSemanticEquivalence`：组 schema、调 LLM、映射布尔到分数 |
| `util.py` | `SQLEquivalenceInput/Output` 与 `SQLEquivalencePrompt` |

## 依赖

- **LLM**：语义等价判断

## 使用示例

```python
metric = SQLSemanticEquivalence(llm=llm)
result = await metric.ascore(
    response="SELECT id, name FROM users WHERE active = true;",
    reference="SELECT id, name FROM users WHERE active = 1;",
    reference_contexts=["Table users: id (INT), name (VARCHAR), active (BOOLEAN)"],
)
```
