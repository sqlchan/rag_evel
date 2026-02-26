# 数据集与实验结果

评估 AI 系统时，通常涉及两类主要数据：

1. **评估数据集**：存放在 `datasets` 目录下。
2. **评估结果**：存放在 `experiments` 目录下。

## 评估数据集

用于评估的数据集包含：

1. **输入**：系统将处理的一组输入。
2. **期望输出（可选）**：系统在给定输入下的期望输出或回答。
3. **元数据（可选）**：可随数据集一起存储的额外信息。

例如，在检索增强生成（RAG）系统中可能包括：查询（系统输入）、评分说明（用于对系统输出评分），以及如查询复杂度等元数据。

元数据对按不同维度切分和分析数据集特别有用。例如，你可以分析系统在复杂查询与简单查询上的表现，或在不同语言上的表现。

## 实验结果

实验结果包括：

1. 数据集中的全部属性。
2. 被评估系统的响应。
3. 各项指标的结果。
4. 可选元数据，例如指向某条输入对应系统追踪的 URI。

例如，在 RAG 系统中，结果可能包括：查询、评分说明、响应、准确率分数（指标）、系统追踪链接等。

## 在 Ragas 中使用数据集

Ragas 提供 `Dataset` 类来操作评估数据集。使用方式如下：

### 创建数据集

```python
from ragas import Dataset

# 创建新数据集
dataset = Dataset(name="my_evaluation", backend="local/csv", root_dir="./data")

# 向数据集添加样本
dataset.append({
    "id": "sample_1",
    "query": "法国的首都是哪里？",
    "expected_answer": "巴黎",
    "metadata": {"complexity": "simple", "language": "en"}
})
```

### 加载已有数据集

```python
# 加载已有数据集
dataset = Dataset.load(
    name="my_evaluation",
    backend="local/csv",
    root_dir="./data"
)
```

### 数据集结构

Ragas 中的数据集结构灵活，可包含评估所需的任意字段。常见字段包括：

- `id`：每个样本的唯一标识
- `query` 或 `input`：输入到 AI 系统的内容
- `expected_output` 或 `ground_truth`：期望响应（如有）
- `metadata`：样本的额外信息

### 数据集创建最佳实践

1. **代表性样本**：确保数据集能代表 AI 系统在真实场景中会遇到的情况。
2. **均衡分布**：在不同难度、主题和边界情况上都有样本。
3. **质量优于数量**：宁可少量高质量、精心整理的样本，也不要大量低质量样本。
4. **元数据丰富**：包含有助于从多维度分析性能的相关元数据。
5. **版本控制**：对数据集变更进行版本管理，保证可复现性。

## 数据集存储与管理

### 本地存储

本地开发和小型数据集可使用 CSV 文件：

```python
dataset = Dataset(name="my_eval", backend="local/csv", root_dir="./datasets")
```

### 云存储

大型数据集或团队协作可考虑云后端：

```python
# Google Drive（实验性）
dataset = Dataset(name="my_eval", backend="gdrive", root_dir="folder_id")

# 可按需添加其他后端
```

### 数据集版本管理

为可复现实验而追踪数据集版本：

```python
# 在数据集名称中包含版本
dataset = Dataset(name="my_eval_v1.2", backend="local/csv", root_dir="./datasets")
```

## 与评估工作流集成

数据集可与 Ragas 评估工作流无缝集成：

```python
from ragas import experiment, Dataset

# 加载数据集
dataset = Dataset.load(name="my_evaluation", backend="local/csv", root_dir="./data")

# 定义实验
@experiment()
async def my_experiment(row):
    # 通过 AI 系统处理输入
    response = await my_ai_system(row["query"])
    
    # 返回用于指标评估的结果
    return {
        **row,  # 包含原始数据
        "response": response,
        "experiment_name": "baseline_v1"
    }

# 在数据集上运行评估
results = await my_experiment.arun(dataset)
```

这样可以在测试数据（数据集）与评估结果（实验）之间保持清晰分离，便于追踪进展和比较不同方案。
