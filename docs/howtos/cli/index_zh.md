# Ragas CLI

Ragas 命令行界面（CLI）提供从终端快速搭建评估项目和运行实验的工具。

## 安装

CLI 随 ragas 包一起安装：

```sh
pip install ragas
```

或使用 `uvx` 无需安装即可运行：

```sh
uvx ragas --help
```

## 可用命令

### `ragas quickstart`

从模板创建完整的评估项目。这是上手 Ragas 最快的方式。

```sh
ragas quickstart [TEMPLATE] [OPTIONS]
```

**参数：**

- `TEMPLATE`：模板名称（可选）。留空可查看可用模板。

**选项：**

- `-o, --output-dir`：创建项目的目录（默认为当前目录）

**示例：**

```sh
# 列出可用模板
ragas quickstart

# 创建 RAG 评估项目
ragas quickstart rag_eval

# 在指定目录创建项目
ragas quickstart rag_eval --output-dir ./my-project
```

### `ragas evals`

使用评估文件对数据集运行评估。

```sh
ragas evals EVAL_FILE [OPTIONS]
```

**参数：**

- `EVAL_FILE`：评估文件路径（必填）

**选项：**

- `--dataset`：项目中数据集的名称（必填）
- `--metrics`：要评估的指标字段名，逗号分隔（必填）
- `--baseline`：用于对比的基线实验名称（可选）
- `--name`：实验运行名称（可选）

**示例：**

```sh
ragas evals evals.py --dataset test_data --metrics accuracy,relevance
```

### `ragas hello_world`

创建简单的 hello world 示例以验证安装。

```sh
ragas hello_world [DIRECTORY]
```

**参数：**

- `DIRECTORY`：创建示例的目录（默认为当前目录）

## Quickstart 模板

### RAG 与检索
- [RAG 评估（`rag_eval`）](rag_eval_zh.md) - 使用自定义指标评估 RAG 系统
- [改进 RAG（`improve_rag`）](improve_rag_zh.md) - 对比朴素 RAG 与智能体式 RAG

### 智能体评估
- [智能体评估（`agent_evals`）](agent_evals_zh.md) - 评估解决数学题的 AI 智能体
- [LlamaIndex 智能体评估（`llamaIndex_agent_evals`）](llamaIndex_agent_evals_zh.md) - 使用工具调用指标评估 LlamaIndex 智能体

### 专项用例
- [Text-to-SQL 评估（`text2sql`）](text2sql_zh.md) - 使用执行准确率评估 text-to-SQL 系统
- [工作流评估（`workflow_eval`）](workflow_eval_zh.md) - 评估复杂 LLM 工作流
- [提示词评估（`prompt_evals`）](prompt_evals_zh.md) - 对比不同提示词变体

### LLM 测试
- [评委对齐（`judge_alignment`）](judge_alignment_zh.md) - 衡量 LLM 作为评委与人类标准的一致性
- [LLM 基准测试（`benchmark_llm`）](benchmark_llm_zh.md) - 对不同 LLM 模型进行基准测试与对比

## 快速开始

60 秒内运行起来：

```sh
# 创建项目
uvx ragas quickstart rag_eval
cd rag_eval

# 安装依赖
uv sync

# 设置 API 密钥
export OPENAI_API_KEY="your-key"

# 运行评估
uv run python evals.py
```

## 下一步

- [RAG 评估指南](rag_eval_zh.md) - rag_eval 模板详细说明
- [改进 RAG 指南](improve_rag_zh.md) - 对比朴素 RAG 与智能体式 RAG
- [自定义指标](../customizations/metrics/_write_your_own_metric_zh.md) - 创建自己的评估指标
