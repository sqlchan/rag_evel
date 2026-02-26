# 如何为你的场景评估新 LLM

当有新 LLM 发布时，你可能想判断它是否在你当前场景下优于现有模型。本指南介绍如何使用 Ragas 在两种模型之间运行准确率对比评估。

## 你将完成的内容

完成本指南后，你将能够：

- 搭建对比两个 LLM 的结构化评估
- 在贴近业务的任务上评估模型表现
- 生成可用于模型选型的详细结果
- 获得可在新模型发布时重复运行的评估流程

## 评估场景

我们以折扣计算为示例：根据客户画像计算合适的折扣比例并说明理由。该任务需要规则应用与推理能力，能区分不同模型的能力。

*说明：你可以将本方法适配到任何对你的应用重要的场景。*

> **📁 完整代码**：示例完整源码见 [Github](https://github.com/vibrantlabsai/ragas/tree/main/examples/benchmark_llm)

## 配置环境与 API

首先安装包含 benchmark LLM 示例的 ragas-examples 包：

```bash
pip install ragas[examples]
```

然后确保已配置 API 凭证：

```bash
export OPENAI_API_KEY=your_actual_api_key
```

## LLM 应用

我们在 examples 包中为你准备了一个简单的 LLM 应用，方便你专注于评估而非实现。该应用根据业务规则计算客户折扣。

下面是定义折扣计算逻辑的系统提示词：

```python
SYSTEM_PROMPT = """
You are a discount calculation assistant. I will provide a customer profile and you must calculate their discount percentage and explain your reasoning.

Discount rules:
- Age 65+ OR student status: 15% discount
- Annual income < $30,000: 20% discount  
- Premium member for 2+ years: 10% discount
- New customer (< 6 months): 5% discount

Rules can stack up to a maximum of 35% discount.

Respond in JSON format only:
{
  "discount_percentage": number,
  "reason": "clear explanation of which rules apply and calculations",
  "applied_rules": ["list", "of", "applied", "rule", "names"]
}
"""
```

可以用示例客户画像测试应用：

```python
from ragas_examples.benchmark_llm.prompt import run_prompt

# Test with a sample customer profile
customer_profile = """
Customer Profile:
- Name: Sarah Johnson
- Age: 67
- Student: No
- Annual Income: $45,000
- Premium Member: Yes, for 3 years
- Account Age: 3 years
"""

result = await run_prompt(customer_profile)
print(result)
```

??? "📋 Output"
    ```json
    {
      "discount_percentage": 25,
      "reason": "Sarah qualifies for a 15% discount due to age (67). She also gets a 10% discount for being a premium member for over 2 years. The total stacking of 15% and 10% discounts results in 25%. No other discounts apply based on income or account age.",
      "applied_rules": ["Age 65+", "Premium member for 2+ years"]
    }
    ```

## 查看评估数据集

本评估使用包含以下类型的合成测试数据集：

- 结果明确的简单案例
- 规则边界的边界案例
- 信息模糊的复杂场景

每条样本包含：

- `customer_profile`：输入数据
- `expected_discount`：期望折扣百分比
- `description`：案例复杂度说明

数据集结构示例（可增加 `id` 列便于对比）：

| ID | Customer Profile | Expected Discount | Description |
|----|------------------|-------------------|-------------|
| 1 | Martha is a 70-year-old retiree who enjoys gardening. She has never enrolled in any academic course recently, has an annual pension of 50,000 dollars, signed up for our service nine years ago and never upgraded to premium. | 15 | Senior only |
| 2 | Arjun, aged 19, is a full-time computer-science undergraduate. His part-time job brings in about 45,000 dollars per year. He opened his account a year ago and has no premium membership. | 15 | Student only |
| 3 | Cynthia, a 40-year-old freelance artist, earns roughly 25,000 dollars a year. She is not studying anywhere, subscribed to our basic plan five years back and never upgraded to premium. | 20 | Low income only |

若要为自己的场景定制数据集，请创建 `datasets/` 目录并放入自己的 CSV 文件。更多说明见 [核心概念 - 评估数据集](../../concepts/components/eval_dataset_zh.md)。

更推荐从应用中抽样真实数据构建数据集。若没有，可用 LLM 生成合成数据。因本场景略复杂，建议使用如 gpt-5-high 这类模型以生成更准确的数据。务必人工审核并校验所用数据。

!!! note
    本示例数据集约 10 条以保持指南简洁。实际评估可先用 20–30 条样本起步，再逐步扩充到 50–100 条以获得更可信的结果。确保覆盖智能体可能遇到的不同场景（含边界与复杂问题）。准确率不必一开始就 100%——用结果做错误分析，迭代提示、数据与工具并持续改进。

### 加载数据集

```python
def load_dataset():
    """Load the dataset from CSV file. Downloads from GitHub if not found locally."""
    import urllib.request
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(current_dir, "datasets", "discount_benchmark.csv")
    # Download dataset from GitHub if it doesn't exist locally
    if not os.path.exists(dataset_path):
        os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
        urllib.request.urlretrieve("https://raw.githubusercontent.com/vibrantlabsai/ragas/main/examples/ragas_examples/benchmark_llm/datasets/discount_benchmark.csv", dataset_path)
    return Dataset.load(name="discount_benchmark", backend="local/csv", root_dir=current_dir)
```

加载逻辑会检查本地是否存在 CSV；若不存在则从 GitHub 自动下载。

### 指标函数

通常使用简单且与场景相关的指标即可。更多指标说明见 [核心概念 - 指标](../../concepts/metrics/index_zh.md)。本评估使用以下准确率指标对每条回答打分：

```python
@discrete_metric(name="discount_accuracy", allowed_values=["correct", "incorrect"])
def discount_accuracy(prediction: str, expected_discount):
    """Check if the discount prediction is correct."""
    import json
    
    parsed_json = json.loads(prediction)
    predicted_discount = parsed_json.get("discount_percentage")
    expected_discount_int = int(expected_discount)
    
    if predicted_discount == expected_discount_int:
        return MetricResult(
            value="correct", 
            reason=f"Correctly calculated discount={expected_discount_int}%"
        )
    else:
        return MetricResult(
            value="incorrect",
            reason=f"Expected discount={expected_discount_int}%; Got discount={predicted_discount}%"
        )
```

### 实验结构

每次模型评估都遵循如下实验模式：

```python
@experiment()
async def benchmark_experiment(row, model_name: str):
    # Get model response
    response = await run_prompt(row["customer_profile"], model=model_name)
    
    # Parse response (strict JSON mode expected)
    try:
        parsed_json = json.loads(response)
        predicted_discount = parsed_json.get('discount_percentage')
    except Exception:
        predicted_discount = None
    
    # Score the response
    score = discount_accuracy.score(
        prediction=response,
        expected_discount=row["expected_discount"]
    )
    
    return {
        **row,
        "model": model_name,
        "response": response,
        "predicted_discount": predicted_discount,
        "score": score.value,
        "score_reason": score.reason
    }
```

## 运行实验

对基线和候选模型分别运行评估实验。示例中对比的模型为：

- 基线：`gpt-4.1-nano-2025-04-14`
- 候选：`gpt-5-nano-2025-08-07`

```python
from ragas_examples.benchmark_llm.evals import benchmark_experiment, load_dataset

# Load dataset
dataset = load_dataset()
print(f"Dataset loaded with {len(dataset)} samples")

# Run baseline experiment
baseline_results = await benchmark_experiment.arun(
    dataset,
    name="gpt-4.1-nano-2025-04-14",
    model_name="gpt-4.1-nano-2025-04-14"
)

# Calculate and display accuracy
baseline_accuracy = sum(1 for r in baseline_results if r["score"] == "correct") / len(baseline_results)
print(f"Baseline Accuracy: {baseline_accuracy:.2%}")

# Run candidate experiment
candidate_results = await benchmark_experiment.arun(
    dataset,
    name="gpt-5-nano-2025-08-07",
    model_name="gpt-5-nano-2025-08-07"
)

# Calculate and display accuracy
candidate_accuracy = sum(1 for r in candidate_results if r["score"] == "correct") / len(candidate_results)
print(f"Candidate Accuracy: {candidate_accuracy:.2%}")
```

每次实验会在 `experiments/` 下保存 CSV，包含每行结果及：id、model、response、predicted_discount、score、score_reason。

??? example "示例实验输出（仅展示部分列以便阅读）"
    | ID | Description | Expected | Predicted | Score | Score Reason |
    |----|-------------|----------|-----------|-------|--------------|
    | 1 | Senior only | 15 | 15 | correct | Correctly calculated discount=15% |
    | 2 | Student only | 15 | 5 | incorrect | Expected discount=15%; Got discount=5% |
    | 3 | Low income only | 20 | 20 | correct | Correctly calculated discount=20% |
    | 4 | Senior, low income, new customer (capped) | 35 | 35 | correct | Correctly calculated discount=35% |
    | 6 | Premium 2+ yrs only | 10 | 15 | incorrect | Expected discount=10%; Got discount=15% |


!!! note
    尽量固定并记录具体模型快照/版本（例如 "gpt-4o-2024-08-06" 而非仅 "gpt-4o"）。厂商会更新别名，不同快照的表现可能不同。可在厂商文档中查看可用快照（如 OpenAI [模型目录](https://platform.openai.com/docs/models)）。在结果中注明快照有利于后续公平、可复现的对比。


## 对比结果

在不同模型上跑完实验后，可并排对比表现：

```python
from ragas_examples.benchmark_llm.evals import compare_inputs_to_output

# Compare the two experiment results
# Update these paths to match your actual experiment output files
output_path = compare_inputs_to_output(
    inputs=[
        "experiments/gpt-4.1-nano-2025-04-14.csv",
        "experiments/gpt-5-nano-2025-08-07.csv"
    ]
)

print(f"Comparison saved to: {output_path}")
```

该对比会：

- 读取两份实验结果文件
- 打印各模型准确率
- 生成并排结果的 CSV

对比文件中包含：

- 测试案例详情（客户画像、期望折扣）
- 每个模型的回答、是否正确及原因

??? "📋 Output"
    ```
    gpt-4.1-nano-2025-04-14 Accuracy: 50.00%
    gpt-5-nano-2025-08-07 Accuracy: 90.00%
    Comparison saved to: experiments/20250820-150548-comparison.csv
    ```

### 用合并 CSV 分析结果

在本示例中：

- 筛选一个模型优于另一个的案例，可得到如 "Senior and new customer"、"Student and new customer"、"Student only"、"Premium 2+ yrs only" 等。
- 各模型回答中的 reason 字段说明其给出该输出的理由。

??? example "对比 CSV 示例行（仅展示部分列）"
    | id | customer_profile | description | expected_discount | gpt-4.1-nano-2025-04-14_score | gpt-5-nano-2025-08-07_score | gpt-4.1-nano-2025-04-14_score_reason | gpt-5-nano-2025-08-07_score_reason | gpt-4.1-nano-2025-04-14_response | gpt-5-nano-2025-08-07_response |
    |---:|---|---|---:|---|---|---|---|---|---|
    | 2 | Arjun, aged 19, is a full-time computer-science undergraduate... | Student only | 15 | incorrect | correct | Expected discount=15%; Got discount=0% | Correctly calculated discount=15% | ... | ... |

!!! tip "新模型发布时重新运行"
    评估脚本一旦纳入项目，即可作为可重复检查。当有新 LLM 发布时，将其作为候选模型接入并重新运行同一评估，与当前基线对比即可。


## 解读结果并做决策

### 关注什么
- **基线准确率** 与 **候选准确率** 及其 **差值**。
  - 本例：基线 50%（5/10），候选 90%（9/10），差值 +40%。

### 如何读每一行
- 浏览两个模型不一致的行。
- 用每行的 score_reason 理解判为正确/错误的原因。
- 总结规律（如漏判规则叠加、边界如“快 65 岁”、收入阈值等）。

### 除准确率外
- 查看 **成本** 和 **延迟**。若候选模型过慢或过贵，高准确率未必值得。

### 做决定
- 若新模型在重要案例上明显更准且满足成本/延迟要求，则切换。
- 若提升有限、失败集中在关键案例或成本/延迟不可接受，则保持现状。

本例中：我们会切换到 "gpt-5-nano-2025-08-07"。它在准确率上从 50% 提升到 90%（+40%），并修正了主要失败模式（漏判规则叠加、边界条件）。若其延迟与成本符合你的约束，可作为更优默认选择。

## 适配到你的场景

要为自己的应用评估模型，可以以 [GitHub 代码](https://github.com/vibrantlabsai/ragas/tree/main/examples/benchmark_llm) 为模板并做适配。

Ragas 会自动处理编排、并行执行与结果汇总，让你把精力放在自己的场景与指标上。
