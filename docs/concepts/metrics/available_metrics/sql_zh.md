# SQL

## 基于执行的指标

这类指标在数据库上执行生成的 SQL 后，将执行结果与期望结果比较，从而比较 `response` 与期望输出。

### DataCompy Score

`DataCompyScore` 使用 DataCompy 库比较两个 pandas DataFrame。`response` 与 `reference` 以 CSV 形式提供，在数据库上执行 response 后将结果与 reference 比较。可通过 `mode` 配置按行（row）或按列（column）比较。默认 mode 为 `row`，指标为精确率与召回率的 F1。详见 [sql.md](sql.md)。

### SQL 语义等价（非执行）

`SQLSemanticEquivalence` 评估生成的 SQL 与参考查询是否语义等价。使用 LLM 在给定数据库 schema 下分析两条查询是否会产出相同结果。二元：1.0 表示等价，0.0 表示不等价。考虑 schema 上下文，可区分语法差异（如 `active = 1` vs `active = true`）。示例与 Legacy `LLMSQLEquivalence` 见 [sql.md](sql.md)。
