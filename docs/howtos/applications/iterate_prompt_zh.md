# 如何评估并改进你的 Prompt

在本指南中，你将学习如何使用 Ragas 对一个 prompt 进行评估，并在此基础上进行迭代改进。

## 你将完成的内容

- 基于评估结果的错误分析，对 prompt 做迭代改进
- 建立清晰的决策标准，在多个 prompt 之间做选择
- 为你的数据集搭建一套可复用的评估流水线
- 学会如何利用 Ragas 搭建这套评估流水线

!!! note "完整代码"
    - 数据集与脚本位于仓库中的 `examples/iterate_prompt/` 目录
    - 完整代码可在 [GitHub](https://github.com/vibrantlabsai/ragas/tree/main/examples/iterate_prompt) 查看

## 任务定义

这里我们以「客服工单分类」任务为例。

- 多标签 `labels`：`Billing`、`Account`、`ProductIssue`、`HowTo`、`Feature`、`RefundCancel`
- 单一优先级 `priority`：`P0`、`P1` 或 `P2`

## 数据集

我们为该场景构造了一份合成数据集。每一行包含 `id, text, labels, priority`。例如：

| id | text                                                                                                                | labels                 | priority |
|----|---------------------------------------------------------------------------------------------------------------------|------------------------|----------|
| 1  | Upgraded to Plus… bank shows two charges the same day; want the duplicate reversed.                                | Billing;RefundCancel   | P1       |
| 2  | SSO via Okta succeeds then bounces back to /login; colleagues can sign in; state mismatch; blocked from boards.    | Account;ProductIssue   | P0       |
| 3  | Need to export a board to PDF with comments and page numbers for audit; deadline next week.                         | HowTo                  | P2       |

如果你要为自己的场景定制数据集，可以创建 `datasets/` 目录并加入自己的 CSV 文件，也可以接入不同存储后端。更多内容参见 [核心概念 - 评估数据集](../../concepts/components/eval_dataset_zh.md)。

更好的做法是直接从你的应用中抽样真实数据构建数据集。如果暂时没有，可使用 LLM 生成合成数据。建议使用具备推理能力的模型（例如 gpt-5 high-reasoning），它能生成更准确、复杂的样本。无论哪种方式，务必人工审阅并验证所使用的数据。

## 在数据集上评估 prompt

### Prompt 运行器

首先，我们先在单个样本上运行 prompt，以确认一切工作正常。

??? example "查看完整 v1 prompt"
    ```text
    You categorize a short customer support ticket into (a) one or more labels and (b) a single priority.
    
    Allowed labels (multi-label):
    - Billing: charges, taxes (GST/VAT), invoices, plans, credits.
    - Account: login/SSO, password reset, identity/email/account merges.
    - ProductIssue: malfunction (crash, error code, won't load, data loss, loops, outages).
    - HowTo: usage questions ("where/how do I…", "where to find…").
    - Feature: new capability or improvement request.
    - RefundCancel: cancel/terminate and/or refund requests.
    - AbuseSpam: insults/profanity/spam (not mild frustration).
    
    Priority (exactly one):
    - P0 (High): blocked from core action or money/data at risk.
    - P1 (Normal): degraded/needs timely help, not fully blocked.
    - P2 (Low): minor/info/how-to/feature.
    
    Return exactly in JSON:
    {"labels":[<labels>], "priority":"P0"|"P1"|"P2"}
    ```

```bash
cd examples/iterate_prompt
export OPENAI_API_KEY=your_openai_api_key
uv run run_prompt.py
```

以上命令会在一个示例工单上运行 prompt，并打印结果。

??? example "输出示例"
    ```
    $ uv run run_prompt.py                      

    Test ticket:
    "SSO via Okta succeeds then bounces me back to /login with no session. Colleagues can sign in. I tried clearing cookies; same result. Error in devtools: state mismatch. I'm blocked from our boards."

    Response:
    {"labels":["Account","ProductIssue"], "priority":"P0"}
    ```

### 评分指标

通常使用**简单**指标比使用过于复杂的指标更好，且指标应与具体场景高度相关。更多指标说明见 [核心概念 - 指标](../../concepts/metrics/index_zh.md)。这里我们使用两个离散指标：`labels_exact_match` 与 `priority_accuracy`。将它们拆开有助于分别分析和修复不同的失败模式。

- `priority_accuracy`：检查预测优先级是否与期望优先级一致，对正确做紧急程度分流非常重要。
- `labels_exact_match`：检查预测标签集合是否与期望标签集合完全一致，有助于避免过度打标或漏标，并衡量整体标签准确率。

```python
# examples/iterate_prompt/evals.py
import json
from ragas.metrics.discrete import discrete_metric
from ragas.metrics.result import MetricResult

@discrete_metric(name="labels_exact_match", allowed_values=["correct", "incorrect"])
def labels_exact_match(prediction: str, expected_labels: str):
    try:
        predicted = set(json.loads(prediction).get("labels", []))
        expected = set(expected_labels.split(";")) if expected_labels else set()
        return MetricResult(
            value="correct" if predicted == expected else "incorrect",
            reason=f"Expected={sorted(expected)}; Got={sorted(predicted)}",
        )
    except Exception as e:
        return MetricResult(value="incorrect", reason=f"Parse error: {e}")

@discrete_metric(name="priority_accuracy", allowed_values=["correct", "incorrect"])
def priority_accuracy(prediction: str, expected_priority: str):
    try:
        predicted = json.loads(prediction).get("priority")
        return MetricResult(
            value="correct" if predicted == expected_priority else "incorrect",
            reason=f"Expected={expected_priority}; Got={predicted}",
        )
    except Exception as e:
        return MetricResult(value="incorrect", reason=f"Parse error: {e}")
```

### 实验函数

实验函数用于在整个数据集上运行 prompt。更多内容参见 [核心概念 - 实验](../../concepts/experimentation_zh.md)。

注意我们将 `prompt_file` 作为参数传入，这样就可以在不同的 prompt 文件之间做实验。你也可以将模型、温度等其他参数传给实验函数，从而探索不同配置。建议在做实验时**一次只修改一个参数**。

```python
# examples/iterate_prompt/evals.py
import asyncio, json
from ragas import experiment
from run_prompt import run_prompt

@experiment()
async def support_triage_experiment(row, prompt_file: str, experiment_name: str):
    response = await asyncio.to_thread(run_prompt, row["text"], prompt_file=prompt_file)
    try:
        parsed = json.loads(response)
        predicted_labels = ";".join(parsed.get("labels", [])) or ""
        predicted_priority = parsed.get("priority")
    except Exception:
        predicted_labels, predicted_priority = "", None

    return {
        "id": row["id"],
        "text": row["text"],
        "response": response,
        "experiment_name": experiment_name,
        "expected_labels": row["labels"],
        "predicted_labels": predicted_labels,
        "expected_priority": row["priority"],
        "predicted_priority": predicted_priority,
        "labels_score": labels_exact_match.score(prediction=response, expected_labels=row["labels"]).value,
        "priority_score": priority_accuracy.score(prediction=response, expected_priority=row["priority"]).value,
    }
```

### 数据集加载器（CSV）

数据集加载器用于将 CSV 数据加载为 Ragas 的 `Dataset` 对象。更多内容参见 [核心概念 - 评估数据集](../../concepts/components/eval_dataset_zh.md)。

```python
# examples/iterate_prompt/evals.py
import os, pandas as pd
from ragas import Dataset

def load_dataset():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(current_dir, "datasets", "support_triage.csv"))
    dataset = Dataset(name="support_triage", backend="local/csv", root_dir=".")
    for _, row in df.iterrows():
        dataset.append({
            "id": str(row["id"]),
            "text": row["text"],
            "labels": row["labels"],
            "priority": row["priority"],
        })
    return dataset
```

### 使用当前 prompt 运行实验

```bash
uv run evals.py run --prompt_file promptv1.txt
```

该命令会在数据集上运行给定 prompt，并将结果保存到 `experiments/` 目录。

??? example "输出示例"
    ```
    $ uv run evals.py run --prompt_file promptv1.txt        
    
    Loading dataset...
    Dataset loaded with 20 samples
    Running evaluation with prompt file: promptv1.txt
    Running experiment: 100%|██████████████████████████████████████████████████████████████████| 20/20 [00:11<00:00,  1.79it/s]
    ✅ promptv1: 20 cases evaluated
    Results saved to: experiments/20250826-041332-promptv1.csv
    promptv1 Labels Accuracy: 80.00%
    promptv1 Priority Accuracy: 75.00%
    ```

## 改进 prompt

### 从结果中分析错误

在你喜欢的表格工具中打开 `experiments/{timestamp}-promptv1.csv`，查看哪些行的 `labels_score` 或 `priority_score` 为错误，然后归纳错误模式。

在 `promptv1` 实验中，我们可以识别出若干模式：

#### 优先级错误：过度提升优先级（P1 → P0）

模型会持续把本应为 P1 的账单相关问题误判为 P0：

| Case | Issue | Expected | Got | Pattern |
|------|-------|----------|-----|---------|
| ID 19 | Auto-charge after pausing workspace | P1 | P0 | Billing dispute treated as urgent |
| ID 1 | Duplicate charge on same day | P1 | P0 | Billing dispute treated as urgent |
| ID 5 | Cancellation with refund request | P1 | P0 | Routine cancellation treated as urgent |
| ID 13 | Follow-up on cancellation | P1 | P0 | Follow-up treated as urgent |

**模式**：模型将所有账单/退款/取消类问题都当作「最高优先级 P0」，而多数其实是日常业务操作（P1）。

#### 标签错误：过度打标与混淆

| Case | Issue | Expected | Got | Pattern |
|------|-------|----------|-----|---------|
| ID 9 | GST tax question from US user | `Billing;HowTo` | `Billing;Account` | 把信息性问题误判为账户操作 |
| ID 10 | Account ownership transfer | `Account` | `Account;Billing` | 只要提到金额/套餐就额外加上 Billing |
| ID 20 | API rate limit question | `ProductIssue;HowTo` | `ProductIssue;Billing;HowTo` | 提到套餐就加 Billing |
| ID 16 | Feature request for offline mode | `Feature` | `Feature;HowTo` | 对于功能请求也加入 HowTo |

**归纳出的模式：**

1. **过度打 Billing 标签**：即便问题并不主要是账单相关，也会加上 `Billing`
2. **HowTo 与 Account 混淆**：将纯「如何做」的问题错判为账号管理操作  
3. **过度打 HowTo 标签**：功能请求中只要用户说了 “how”，就被误标为 `HowTo`

### 改进 prompt

基于上述错误分析，我们创建新的 `promptv2_fewshot.txt`，加入针对性的改进。可以用 LLM 帮助生成新版 prompt，也可以手工修改。在本例中，我们把错误模式与原始 prompt 一并给到 LLM，请它生成带 few-shot 示例的改写版本。

#### `promptv2_fewshot` 的关键新增内容

**1. 更强调业务影响的优先级规则：**
```
- P0: Blocked from core functionality OR money/data at risk OR business operations halted
- P1: Degraded experience OR needs timely help BUT has workarounds OR not fully blocked  
- P2: Minor issues OR information requests OR feature requests OR non-urgent how-to
```

**2. 保守的多标签规则，避免过度打标：**
```
## Multi-label Guidelines
Use single label for PRIMARY issue unless both aspects are equally important:
- Billing + RefundCancel: Always co-label. Cancellation/refund requests must include Billing.  
- Account + ProductIssue: For auth/login malfunctions (loops, "invalid_token", state mismatch, bounce-backs)
- Avoid adding Billing to account-only administration unless there is an explicit billing operation

Avoid over-tagging: Focus on which department should handle this ticket first.
```

**3. 更详细的优先级指引与具体场景：**
```
## Priority Guidelines  
- Ignore emotional tone - focus on business impact and available workarounds
- Billing disputes/adjustments (refunds, duplicate charges, incorrect taxes/pricing) = P1 unless causing an operational block
- Login workarounds: If Incognito/another account works, prefer P1; if cannot access at all, P0
- Core business functions failing (webhooks, API, sync) = P0
```

**4. 带推理说明的完整示例：**

加入 7 个带推理说明的示例，展示不同场景下的正确分类方式：

```md
## Examples with Reasoning

Input: "My colleague left and I need to change the team lead role to my email address."
Output: {"labels":["Account"], "priority":"P1"}
Reasoning: Administrative role change; avoid adding Billing unless a concrete billing action is requested.

Input: "Dashboard crashes when I click reports tab, but works fine in mobile app."
Output: {"labels":["ProductIssue"], "priority":"P1"}
Reasoning: Malfunction exists but workaround available (mobile app works); single label since primary issue is product malfunction.
```

!!! tip "避免直接把评估数据集里的样本原封不动放进 few-shot"
    否则容易对该数据集过拟合，导致在其他真实数据上的表现变差。

### 评估新 prompt

编写好 `promptv2_fewshot.txt` 后，用它重新运行实验：

```bash
uv run evals.py run --prompt_file promptv2_fewshot.txt
```

这会在同一数据集上评估改进版 prompt，并将结果保存到新的带时间戳的 CSV 文件。

??? example "输出示例"
    ```
    $ uv run evals.py run --prompt_file promptv2_fewshot.txt
    
    Loading dataset...
    Dataset loaded with 20 samples
    Running evaluation with prompt file: promptv2_fewshot.txt
    Running experiment: 100%|██████████████████████████████████████████████████████████████| 20/20 [00:11<00:00,  1.75it/s]
    ✅ promptv2_fewshot: 20 cases evaluated
    Results saved to: experiments/20250826-231414-promptv2_fewshot.csv
    promptv2_fewshot Labels Accuracy: 90.00%
    promptv2_fewshot Priority Accuracy: 95.00%
    ```

实验会在 `experiments/` 目录中生成一个新的 CSV 文件，结构与第一次运行相同，便于直接对比。

### 分析并对比结果

我们提供了一个小工具函数，可以将多个 CSV 合并，方便比较：

```bash
uv run evals.py compare --inputs experiments/20250826-041332-promptv1.csv experiments/20250826-231414-promptv2_fewshot.csv 
```

该命令会打印每次实验的准确率，并在 `experiments/` 目录保存一份合并后的 CSV。

??? Sample output
    ```bash
    $ uv run evals.py compare --inputs experiments/20250826-041332-promptv1.csv experiments/20250826-231414-promptv2_fewshot.csv 

    promptv1 Labels Accuracy: 80.00%
    promptv1 Priority Accuracy: 75.00%
    promptv2_fewshot Labels Accuracy: 90.00%
    promptv2_fewshot Priority Accuracy: 95.00%
    Combined comparison saved to: experiments/20250826-231545-comparison.csv
    ```

可以看到，`promptv2_fewshot` 在标签与优先级两个维度的准确率都有明显提升。但仍有部分样本失败，你可以继续对这些错误做分析并进一步改进 prompt。

当改进效果趋于平缓（准确率提升极小），或已达到业务预期时，就可以停止迭代。

!!! tip "如果仅通过 prompt 调整已无法明显提升准确率，可以尝试使用更强的模型"

## 将这套循环应用到你的场景

- 为你的场景创建数据集、指标与实验函数
- 运行评估并分析错误
- 根据错误分析结果改进 prompt
- 再次运行评估并对比结果
- 当提升趋于平缓或达到业务要求时收敛

当你有了数据集与评估循环后，就可以顺势扩展到更多参数（例如模型、温度等）的实验。

Ragas 会帮你处理编排、并行执行与结果汇总，让你能够把精力集中在「场景本身」而非基础设施上。

!!! tip "进阶：先对齐 LLM 评判者再做评估"
    如果你用 LLM 作为评估指标（如上述离散指标背后的 LLM），建议先将这个「LLM 评判者」与人类专家对齐，以获得更可靠的评估。可参考 [如何将 LLM 对齐为评判](../applications/align-llm-as-judge_zh.md)。

