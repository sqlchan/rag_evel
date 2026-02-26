# Ragas Optimizers 模块功能说明

本模块提供基于 Ragas 指标的 **提示词（Prompt）优化器**，用于在给定标注数据集和损失函数下，自动搜索或演化出更优的 prompt，以提升评估指标表现。

---

## 一、模块结构概览

| 文件 | 职责 |
|------|------|
| `base.py` | 优化器抽象基类，定义统一接口 `optimize()` |
| `utils.py` | 工具函数：汉明距离等，用于遗传算法中的个体差异度量 |
| `genetic.py` | 遗传算法优化器：种群初始化、反馈变异、交叉变异、适应度评估 |
| `dspy_adapter.py` | DSPy 适配层：Ragas Prompt/数据集/损失 与 DSPy 的转换与 LLM 配置 |
| `dspy_llm_wrapper.py` | 将 Ragas LLM 包装成 DSPy 可调用的 LM 接口 |
| `dspy_optimizer.py` | 基于 DSPy MIPROv2 的优化器实现 |
| `__init__.py` | 导出 `Optimizer`、`GeneticOptimizer`，可选导出 `DSPyOptimizer` |

---

## 二、base.py：优化器基类

- **作用**：所有优化器的抽象基类。
- **核心接口**：
  - `optimize(dataset, loss, config, run_config, ...) -> Dict[str, str]`
    - 输入：单指标标注数据集 `SingleMetricAnnotation`、损失 `Loss`、配置字典等。
    - 输出：优化后的 prompt 字典，key 为 prompt 名称，value 为指令字符串。
- **依赖**：需要子类提供 `metric`（带 LLM 的指标）和 `llm`，在具体优化器中用于执行评估与生成。

---

## 三、utils.py：工具函数

- **`hamming_distance(vectors: np.ndarray) -> np.ndarray`**
  - 计算多组向量两两之间的 **汉明距离**（对应位置不同的个数）。
  - 要求所有向量维度一致。
  - 在遗传优化器中用于根据「预测向量」的差异构建距离矩阵，从而选择「差异大」的个体做交叉，增加多样性。

---

## 四、genetic.py：遗传算法优化器

### 4.1 整体流程

`GeneticOptimizer.optimize()` 大致分为四步：

1. **初始化种群（Initializing Population）**
   - 从已接受（`is_accepted`）的标注中按 `metric_output` 分层抽样，组成若干批「输入-输出」示例。
   - 用 **逆向工程 prompt**（`ReverseEngineerPrompt`）根据示例反推指令，得到多条候选指令，构成初始种群的一部分。
   - 再加上当前 metric 的默认 prompt 作为种子，共同组成初始种群。

2. **反馈变异（Feedback Mutation）**
   - 对每个候选 prompt 在数据集子集上做评估，得到预测与真实标签。
   - 找出预测错误的样本，用 **反馈生成 prompt**（`FeedbackMutationPrompt`）让 LLM 给出「如何改指令才能得到期望输出」的反馈。
   - 再用 **反馈应用 prompt**（`FeedbackMutationPromptGeneration`）根据反馈生成新指令，实现「反馈变异」。

3. **交叉变异（Cross-over Mutation）**
   - 对所有候选在完整标注集上评估，得到每个样本上的对/错，组成 0/1 预测向量。
   - 用 `hamming_distance` 计算候选两两之间的汉明距离。
   - 对每个个体，选与之汉明距离**最小**的另一个体作为配对，用 **交叉 prompt**（`CrossOverPrompt`）将两条指令「杂交」成一条新指令，得到子代种群。

4. **适应度评估（Fitness Evaluation）**
   - 对当前所有候选在标注集上跑一次评估，用传入的 `loss(y_true, y_pred)` 计算损失。
   - 取损失**最小**（适应度最高）的候选作为最终优化结果并返回。

### 4.2 关键数据与 Prompt 类型

- **FormattedExamples / ReverseEngineerPrompt**：把 (输入, 期望输出) 格式化为统一文本，让 LLM 反推「标注员看到的指令」。
- **ParentPrompts / CrossOverPrompt**：两条父指令，生成一条融合语义的子代指令。
- **FeedbackMutationInput/Output、FeedbackMutationPrompt**：根据指令 + (输入, 输出, 期望输出) 示例，生成改进指令的反馈列表。
- **FeedbackMutationPromptInput、FeedbackMutationPromptGeneration**：根据指令 + 反馈列表，生成融入反馈的新指令。

### 4.3 配置项（config 字典）

- `population_size`：种群大小（默认 3）。
- `num_demonstrations`：逆向工程时每批示例数量（默认 3）。
- `sample_size`：反馈变异时从数据集中采样的样本数（默认 12）。

---

## 五、DSPy 相关：dspy_adapter / dspy_llm_wrapper / dspy_optimizer

### 5.1 dspy_llm_wrapper.py：Ragas LLM → DSPy LM

- **RagasDSPyLM**：包装 `BaseRagasLLM`，实现 DSPy 期望的调用方式。
- **`__call__(prompt=None, messages=None, **kwargs) -> List[str]`**：支持单条 `prompt` 或 `messages`，内部转成 Ragas 的 `PromptValue`，调用 `ragas_llm.generate()`，返回生成的文本列表。
- **`inspect_history(n)`**：返回最近 n 次调用的历史，便于调试。

### 5.2 dspy_adapter.py：Ragas ↔ DSPy 转换

- **setup_dspy_llm(dspy, ragas_llm)**：用 `RagasDSPyLM` 包装 Ragas LLM，并设为 `dspy.settings` 的默认 LM。
- **pydantic_prompt_to_dspy_signature(prompt)**：将 Ragas 的 `PydanticPrompt`（含 `input_model`、`output_model`、`instruction`）转成 DSPy 的 `Signature` 类（InputField/OutputField + doc 为 instruction）。
- **ragas_dataset_to_dspy_examples(dataset, prompt_name)**：从 `SingleMetricAnnotation` 中取出 `is_accepted` 的样本，按 `prompt_name` 抽取 `prompt_input` 与 `prompt_output`（或 `edited_output`），构造成 `dspy.Example` 列表。
- **create_dspy_metric(loss, metric_name)**：将 Ragas 的 `Loss(y_true, y_pred)` 封装成 DSPy 的 `metric(example, prediction) -> float`，且 **分数越高越好**（内部对 loss 取负）。

### 5.3 dspy_optimizer.py：DSPy MIPROv2 优化器

- **DSPyOptimizer**：继承 `Optimizer`，使用 DSPy 的 **MIPROv2** 做指令与 demo 的联合优化。
- **optimize() 流程**：
  1. 若启用 cache，先根据数据集/损失/配置生成 cache key，命中则直接返回缓存结果。
  2. 对 metric 的每个 prompt：转成 DSPy Signature → 用 `dspy.Predict(signature)` 建模块 → 将 Ragas 数据集转成 DSPy examples → 用 `create_dspy_metric(loss, dataset.name)` 得到 DSPy metric。
  3. 使用 `MIPROv2`（可配置 num_candidates、max_bootstrapped_demos、max_labeled_demos、temperature、auto 等）对模块进行 `compile(trainset=examples, metric=metric_fn)`。
  4. 从编译后的模块中 `_extract_instruction()` 抽出优化后的指令字符串，汇总成 `Dict[str, str]`。
  5. 若启用 cache，将结果写入缓存。
- **参数要点**：`num_candidates`、`max_bootstrapped_demos`、`max_labeled_demos`、`init_temperature`、`auto`（light/medium/heavy）、`seed`、`cache`、`metric_threshold` 等，详见类文档字符串。
- **缓存**：`_generate_cache_key()` 使用 metric 名、数据集哈希、loss 名、优化器参数等生成 SHA256，保证相同输入得到相同 key。

---

## 六、使用方式简述

- **遗传优化器**：适合无 DSPy 依赖、希望用「逆向工程 + 反馈 + 交叉」演化 prompt 的场景；需提供 `metric`、`llm` 和足够量的标注（如至少 10 条 `is_accepted`）。
- **DSPy 优化器**：需安装 `ragas[dspy]`，利用 MIPROv2 做更系统的指令与示例搜索；同样需要 `metric`、`llm` 和标注数据。

两种优化器都通过统一的 `optimize(dataset, loss, config, ...)` 返回优化后的 prompt 字典，可用于更新 metric 的 prompt 或后续评估。
