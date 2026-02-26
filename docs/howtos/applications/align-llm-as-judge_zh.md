# 如何将 LLM 对齐为评判（Judge）

本指南介绍如何使用 Ragas 系统性地评估并将“LLM 即评判”指标与人类专家判断对齐。

- 搭建可复用的评判对齐评估流水线
- 分析评判与人工标签之间的不一致模式
- 迭代评判提示词以提升与专家决策的对齐度

## 为何要先对齐 LLM 评判？

在跑评估实验之前，先把 LLM 评判对齐到你的具体场景很重要。未对齐的评判就像指错方向的指南针——基于它的指导所做的“改进”会离目标更远。让评判与专家判断一致，才能改进真正重要的维度。对齐步骤是可靠评估的基础。

!!! tip "真正价值：看你的数据"
    构建一个对齐的 LLM 评判有用，但真正的业务价值来自系统性地分析数据、理解失败模式。评判对齐过程会迫使你深入审视边界案例、澄清评估标准，并发现“什么算好/坏回答”的洞察。把评判当作放大分析能力的工具，而不是替代分析本身。

## 配置环境

我们准备了一个可安装运行的简单模块，方便你专注于理解评估流程而非从零写应用。

```bash
uv pip install "ragas[examples]"
export OPENAI_API_KEY="your-api-key-here"
```

!!! note "完整代码"
    评判对齐评估流水线的完整代码见[此处](https://github.com/vibrantlabsai/ragas/tree/main/examples/ragas_examples/judge_alignment)。

## 理解数据集

我们使用 [EvalsBench 数据集](https://github.com/vibrantlabsai/EvalsBench/blob/main/data/benchmark_df.csv)，其中包含针对商业问题的 LLM 回答及专家标注。每行包括：

- `question`：原始问题
- `grading_notes`：好回答应涵盖的要点
- `response`：LLM 生成的回答
- `target`：人类专家的二值判断（pass/fail）

**下载数据集：**

```bash
# Create datasets folder and download the dataset
mkdir -p datasets
curl -o datasets/benchmark_df.csv https://raw.githubusercontent.com/vibrantlabsai/EvalsBench/main/data/benchmark_df.csv
```

**加载并查看数据集：**

```python
import pandas as pd
from ragas import Dataset

def load_dataset(csv_path: str = None) -> Dataset:
    """Load annotated dataset with human judgments.
    
    Expected columns: question, grading_notes, response, target (pass/fail)
    """
    path = csv_path or "datasets/benchmark_df.csv"
    df = pd.read_csv(path)

    dataset = Dataset(name="llm_judge_alignment", backend="local/csv")
    
    for _, row in df.iterrows():
        dataset.append({
            "question": row["question"],
            "grading_notes": row["grading_notes"],
            "response": row["response"],
            "target": (row["target"]),
        })
    
    return dataset

# Load the dataset
dataset = load_dataset()
print(f"Dataset loaded with {len(dataset)} samples")
```

**数据集示例行：**

| question | grading_notes | response | target |
|----------|---------------|----------|---------|
| What are the key methods for determining the pre-money valuation of a tech startup before a Series A investment round, and how do they differ? | DCF method: !future cash flows!, requires projections; Comp. analysis: similar co. multiples; VC method: rev x multiple - post-$; *Founder's share matter*; strategic buyers pay more. | Determining the pre-money valuation of a tech startup before a Series A investment round is a critical step... (covers DCF, comparable analysis, VC method) | pass |
| What key metrics and strategies should a startup prioritize to effectively manage and reduce churn rate in a subscription-based business model? | Churn:! monitor monthly, <5% ideal. *Retention strategies*: engage users, improve onboarding. CAC & LTV: balance 3:1+. Feedback loops: implement early. *Customer support*: proactive & responsive, critical. | Managing and reducing churn rate in a subscription-based business model is crucial... (missing specific metrics and strategies) | fail |

数据集中同一问题有多条回答——有的 pass、有的 fail，有助于评判学习“可接受”与“不可接受”的细微差别。

!!! info "理解你的标准答案"
    评判对齐的质量完全取决于标准答案（ground truth）标签的质量。在生产场景中，应让**领域主专家**参与——即对你场景最重要的那个人（如心理健康 AI 用心理学家、法律 AI 用律师、客服聊天机器人用客服总监）。他们稳定一致的判断应成为评判对齐的金标准。不需要给每条样本都打标，有代表性的 100–200 条覆盖多种场景即可获得可靠对齐。

## 理解评估方式

本指南中对数据集中已有的回答做评估，而不是重新生成。这样保证多次运行可复现，并让我们专注于评判对齐而非生成。

评估流程：**数据行（问题 + 回答）→ 评判 → 与人类 target 对比**

## 定义评估指标

评判对齐需要两个指标：

**主指标：`accuracy`（LLM 评判）** — 对回答打分并返回 pass/fail 及理由。

**对齐指标：`judge_alignment`** — 检查评判结论是否与人类专家一致。

### 配置评判指标

定义一个根据 grading notes 评估回答的简单基线评判指标：

```python
from ragas.metrics import DiscreteMetric

# Define the judge metric with a simple baseline prompt
accuracy_metric = DiscreteMetric(
    name="accuracy",
    prompt="Check if the response contains points mentioned from the grading notes and return 'pass' or 'fail'.\n\nResponse: {response}\nGrading Notes: {grading_notes}",
    allowed_values=["pass", "fail"],
)
```

### 对齐指标

对齐指标将评判结论与人类结论比较：

```python
from ragas.metrics.discrete import discrete_metric
from ragas.metrics.result import MetricResult

@discrete_metric(name="judge_alignment", allowed_values=["pass", "fail"])
def judge_alignment(judge_label: str, human_label: str) -> MetricResult:
    """Compare judge decision with human label."""
    judge = judge_label.strip().lower()
    human = human_label.strip().lower()
    
    if judge == human:
        return MetricResult(value="pass", reason=f"Judge={judge}; Human={human}")
    
    return MetricResult(value="fail", reason=f"Judge={judge}; Human={human}")
```

## 实验函数

[实验函数](../../concepts/experimentation_zh.md) 负责完整评估流水线：用评判对回答打分并测量与人类的对齐度：

```python
from typing import Dict, Any
from ragas import experiment
from ragas.metrics import DiscreteMetric
from ragas_examples.judge_alignment import judge_alignment  # The metric we created above

@experiment()
async def judge_experiment(
    row: Dict[str, Any],
    accuracy_metric: DiscreteMetric,
    llm,
):
    """Run complete evaluation: Judge → Compare with human."""
    # Step 1: Get response (in production, this is where you'd call your LLM app)
    # For this evaluation, we use pre-existing responses from the dataset
    app_response = row["response"]
    
    # Step 2: Judge evaluates the response
    judge_score = await accuracy_metric.ascore(
        question=row["question"],
        grading_notes=row["grading_notes"],
        response=app_response,
        llm=llm,
    )

    # Step 3: Compare judge decision with human target
    alignment = judge_alignment.score(
        judge_label=judge_score.value,
        human_label=row["target"]
    )

    return {
        **row,
        "judge_label": judge_score.value,
        "judge_reason": judge_score.reason,
        "alignment": alignment.value,
        "alignment_reason": alignment.reason,
    }
```

## 运行基线评估

### 执行评估流水线并收集结果

```python
import os
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas_examples.judge_alignment import load_dataset

# Load dataset
dataset = load_dataset()
print(f"Dataset loaded with {len(dataset)} samples")

# Initialize LLM client
openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
llm = llm_factory("gpt-4o-mini", client=openai_client)

# Run the experiment
results = await judge_experiment.arun(
    dataset,
    name="judge_baseline_v1_gpt-4o-mini",
    accuracy_metric=accuracy_metric,
    llm=llm,
)

# Calculate alignment rate
passed = sum(1 for r in results if r["alignment"] == "pass")
total = len(results)
print(f"✅ Baseline alignment: {passed}/{total} passed ({passed/total:.1%})")
```

??? "📋 Output (baseline v1)"

    ```text
    2025-10-08 22:40:00,334 - Loaded dataset with 160 samples
    2025-10-08 22:40:00,334 - Initializing LLM client with model: gpt-4o-mini
    2025-10-08 22:40:01,858 - Running baseline evaluation...
    Running experiment: 100%|████████████████████████| 160/160 [04:35<00:00,  1.72s/it]
    2025-10-08 22:44:37,149 - ✅ Baseline alignment: 121/160 passed (75.6%)
    ```

### 初步表现分析

评估会生成包含所有输入（question、grading_notes、response）、人类 target、评判结论及理由以及对齐比较的 CSV 结果。

## 分析错误与失败模式

跑完基线评估后，可以分析不一致模式，看评判在哪些地方与专家不一致。

**基线表现：75.6% 对齐（121/160 正确）**

查看错误分布：

??? admonition "📋 Code"

    ```python
    import pandas as pd

    # Load results
    df = pd.read_csv('experiments/judge_baseline_v1_gpt-4o-mini.csv')

    # Analyze misalignments
    false_positives = len(df[(df['judge_label'] == 'pass') & (df['target'] == 'fail')])
    false_negatives = len(df[(df['judge_label'] == 'fail') & (df['target'] == 'pass')])

    print(f"False positives (judge too lenient): {false_positives}")
    print(f"False negatives (judge too strict): {false_negatives}")
    ```

    📋 Output

    ```text
    False positives (judge too lenient): 39
    False negatives (judge too strict): 0
    ```

**主要结论：** 全部 39 个不一致（24.4%）都是假阳性——评判给了 pass 而专家给了 fail。基线评判过于宽松，漏掉了未涵盖 grading notes 中关键概念的回答。

### 失败案例示例

以下为评判错误地给了 pass、但缺少关键概念的回答示例：

| Grading Notes | Human Label | Judge Label | What's Missing |
|---------------|-------------|-------------|----------------|
| `*Valuation caps*, $, post-$ val key. Liquidation prefs: 1x+ common. Anti-dilution: *full vs. weighted*. Board seats: 1-2 investor reps. ESOP: 10-20%.` | fail | pass | Response discusses all points comprehensively but human annotators marked it as fail for subtle omissions |
| `*Impact on valuation*: scalability potential, dev costs, integration ease. !Open-source vs proprietary issues. !Tech debt risks. Discuss AWS/GCP/Azure...` | fail | pass | Missing specific discussion of post-money valuation impact |
| `Historical vs. forecasted rev; top-down & bottom-up methods; *traction evidence*; !unbiased assumptions; 12-24mo project...` | fail | pass | Missing explicit mention of traction evidence |

**错误中的常见模式：**

1. **缺少 1–2 个具体概念**，其他概念都有
2. **隐含 vs 显式**：评判接受了隐含表述，而我们希望显式提到
3. **缩写未正确解析**（如 "mkt demand" = market demand，"post-$" = post-money valuation）
4. **忽略关键标记**：带 `*` 或 `!` 的要点往往必不可少

## 改进评判提示词

根据错误分析，需要构造一个改进版提示词，要求：

1. **理解** grading notes 中的缩写
2. **识别关键标记**（`*`、`!`、具体数字）
3. **要求所有概念**都出现，而不是大部分
4. **接受语义等价**（同一概念的不同表述）
5. **松紧适中**——既不过松也不过严

### 编写改进版 v2 提示词

用更完整的评估标准定义增强版评判指标：

```python
from ragas.metrics import DiscreteMetric

# Define improved judge metric with enhanced evaluation criteria
accuracy_metric_v2 = DiscreteMetric(
    name="accuracy",
    prompt="""Evaluate if the response covers ALL the key concepts from the grading notes. Accept semantic equivalents but carefully check for missing concepts.

ABBREVIATION GUIDE - decode these correctly:

• Financial: val=valuation, post-$=post-money, rev=revenue, ARR/MRR=Annual/Monthly Recurring Revenue, COGS=Cost of Goods Sold, Opex=Operating Expenses, LTV=Lifetime Value, CAC=Customer Acquisition Cost
• Business: mkt=market, reg/regs=regulation/regulatory, corp gov=corporate governance, integr=integration, S&M=Sales & Marketing, R&D=Research & Development, acq=acquisition
• Technical: sys=system, elim=elimination, IP=Intellectual Property, TAM=Total Addressable Market, diff=differentiation
• Metrics: NPS=Net Promoter Score, SROI=Social Return on Investment, proj=projection, cert=certification

EVALUATION APPROACH:

Step 1 - Parse grading notes into distinct concepts:

- Separate by commas, semicolons, or line breaks
- Each item is a concept that must be verified
- Example: "*Gross Margin* >40%, CAC, LTV:CAC >3:1" = 3 concepts

Step 2 - For each concept, check if it's addressed:

- Accept semantic equivalents (e.g., "customer acquisition cost" = "CAC")
- Accept implicit coverage when it's clear (e.g., "revenue forecasting" covers "historical vs forecasted rev")
- Be flexible on exact numbers (e.g., "around 40%" acceptable for ">40%")

Step 3 - Count missing concepts:

- Missing 0 concepts = PASS
- Missing 1+ concepts = FAIL (even one genuinely missing concept should fail)
- Exception: If a long list (10+ items) has 1 very minor detail missing but all major points covered, use judgment

CRITICAL RULES:

1. Do NOT require exact wording - "market demand" = "mkt demand" = "demand analysis"

2. Markers (* or !) mean important, not mandatory exact phrases:
   - "*traction evidence*" can be satisfied by discussing metrics, growth, or validation
   - "!unbiased assumptions" can be satisfied by discussing assumption methodology

3. Numbers should be mentioned but accept approximations:
   - "$47B to $10B" can be "$47 billion dropped to around $10 billion"
   - "LTV:CAC >3:1" can be "LTV to CAC ratio of at least 3 to 1" or "3x or higher"

4. FAIL only when concepts are genuinely absent:
   - If notes mention "liquidation prefs, anti-dilution, board seats" but response only has board seats → FAIL
   - If notes mention "scalability, tech debt, IP" but response never discusses technical risks → FAIL
   - If notes mention "GDPR compliance" and response never mentions GDPR or EU regulations → FAIL

5. PASS when ALL concepts present:
   - All concepts covered, even with different wording → PASS
   - Concepts addressed implicitly when clearly implied → PASS
   - Minor phrasing differences → PASS
   - One or more concepts genuinely absent → FAIL

Response: {response}

Grading Notes: {grading_notes}

Are ALL distinct concepts from the grading notes covered in the response (accepting semantic equivalents and implicit coverage)?""",
    allowed_values=["pass", "fail"],
)
```

!!! tip "用 LLM 优化提示词"
    在清晰识别错误模式后，可以用 LLM 优化提示词。也可以用 LLM 辅助找错误，但需人工复核以与标准答案一致。还可使用 Cursor、Claude Code 等编程智能体或 [DSPy](https://github.com/stanfordnlp/dspy) 等框架系统性地优化评判提示词。

## 用改进后的提示词重新运行评估

用增强的 v2 提示词再跑一遍评估（配置与基线相同，仅替换指标）：

```python
# Use the same dataset and LLM setup from the baseline evaluation above
results = await judge_experiment.arun(
    dataset,
    name="judge_accuracy_v2_gpt-4o-mini",
    accuracy_metric=accuracy_metric_v2,  # ← Using improved v2 prompt
    llm=llm,
)

passed = sum(1 for r in results if r["alignment"] == "pass")
total = len(results)
print(f"✅ V2 alignment: {passed}/{total} passed ({passed/total:.1%})")
```

??? "📋 Output (improved v2)"

    ```text
    2025-10-08 23:42:11,650 - Loaded dataset with 160 samples
    2025-10-08 23:42:11,650 - Initializing LLM client with model: gpt-4o-mini
    2025-10-08 23:42:12,730 - Running v2 evaluation with improved prompt...
    Running experiment: 100%|██████████| 160/160 [04:39<00:00,  1.75s/it]
    2025-10-08 23:46:52,740 - ✅ V2 alignment: 139/160 passed (86.9%)
    ```

**明显提升：** 对齐率从 75.6% 提高到 86.9%。

若需继续迭代：

- 分析剩余错误、归纳模式（是假阳性还是假阴性？）
- 在标签旁标注你的推理，便于改进 LLM 评判，也可作为 few-shot 示例
- **使用更强模型**：如 GPT-5、Claude 4.5 Sonnet 等通常作为评判更稳
- **借助 AI 助手**：本指南即用 Cursor AI 分析失败并迭代提示词。可使用 Cursor、Claude 等编程智能体或 [DSPy](https://github.com/stanfordnlp/dspy) 系统优化评判提示词
- 当对齐在 2–3 轮迭代后趋于稳定或达到业务阈值时即可停止

## 你已完成的内容

你已用 Ragas 搭建了一个系统化的评估流水线，能够：

- 用清晰指标衡量评判与专家判断的对齐度
- 通过结构化错误分析识别失败模式
- 在可复现实验中跟踪多次运行的改进

这个对齐好的评判将成为你可靠 AI 评估的基础。有了可信的评判，就可以放心地评估 RAG 流水线、智能体工作流或任何 LLM 应用——指标提升将对应真实的质量提升。
