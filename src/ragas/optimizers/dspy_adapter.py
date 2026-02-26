import typing as t

from ragas.dataset_schema import SingleMetricAnnotation
from ragas.llms.base import BaseRagasLLM
from ragas.losses import Loss
from ragas.prompt.pydantic_prompt import PydanticPrompt


def setup_dspy_llm(dspy: t.Any, ragas_llm: BaseRagasLLM) -> None:
    """
    将 Ragas LLM 包装为 DSPy 可用的 LM，并设为 DSPy 全局默认 LM。
    Configure DSPy to use Ragas LLM.
    """
    from ragas.optimizers.dspy_llm_wrapper import RagasDSPyLM

    lm = RagasDSPyLM(ragas_llm)
    dspy.settings.configure(lm=lm)


def pydantic_prompt_to_dspy_signature(
    prompt: PydanticPrompt[t.Any, t.Any],
) -> t.Type[t.Any]:
    """
    将 Ragas 的 PydanticPrompt（input_model/output_model/instruction）转为 DSPy 的 Signature 类。
    Convert Ragas PydanticPrompt to DSPy Signature.
    """
    try:
        import dspy
    except ImportError as e:
        raise ImportError(
            "DSPy optimizer requires dspy-ai. Install with:\n"
            "  uv add 'ragas[dspy]'  # or: pip install 'ragas[dspy]'\n"
        ) from e

    fields = {}

    # 输入字段 → dspy.InputField
    for name, field_info in prompt.input_model.model_fields.items():
        fields[name] = dspy.InputField(
            desc=field_info.description or "",
        )

    # 输出字段 → dspy.OutputField
    for name, field_info in prompt.output_model.model_fields.items():
        fields[name] = dspy.OutputField(
            desc=field_info.description or "",
        )

    # 动态创建 Signature 子类，__doc__ 存 instruction
    signature_class = type(
        f"{prompt.__class__.__name__}Signature",
        (dspy.Signature,),
        {"__doc__": prompt.instruction, **fields},
    )

    return signature_class


def ragas_dataset_to_dspy_examples(
    dataset: SingleMetricAnnotation,
    prompt_name: str,
) -> t.List[t.Any]:
    """
    从 Ragas 单指标标注数据集中按 prompt 名称抽取 (输入, 输出)，转为 DSPy Example 列表。
    Convert Ragas annotated dataset to DSPy examples.
    """
    try:
        import dspy
    except ImportError as e:
        raise ImportError(
            "DSPy optimizer requires dspy-ai. Install with:\n"
            "  uv add 'ragas[dspy]'  # or: pip install 'ragas[dspy]'\n"
        ) from e

    examples = []

    for sample in dataset:
        if not sample["is_accepted"]:
            continue

        prompt_data = sample["prompts"].get(prompt_name)

        if prompt_data is None:
            continue

        prompt_input = prompt_data["prompt_input"]
        # 优先使用人工编辑后的输出
        prompt_output = (
            prompt_data["edited_output"]
            if prompt_data["edited_output"]
            else prompt_data["prompt_output"]
        )

        example_dict = {**prompt_input}
        if isinstance(prompt_output, dict):
            example_dict.update(prompt_output)
        else:
            example_dict["output"] = prompt_output

        # 标记哪些键为输入，其余为输出
        input_keys = list(prompt_input.keys())
        example = dspy.Example(**example_dict).with_inputs(*input_keys)
        examples.append(example)

    return examples


def create_dspy_metric(
    loss: Loss, metric_name: str
) -> t.Callable[[t.Any, t.Any], float]:
    """
    将 Ragas 的 Loss(y_true, y_pred) 封装成 DSPy 的 metric(example, prediction)；
    DSPy 约定分数越高越好，故对 loss 取负。
    Convert Ragas Loss function to DSPy metric (higher is better).
    """

    def dspy_metric(example: t.Any, prediction: t.Any) -> float:
        ground_truth = getattr(example, metric_name, None)
        predicted = getattr(prediction, metric_name, None)

        if ground_truth is None or predicted is None:
            return 0.0

        loss_value = loss([predicted], [ground_truth])
        # DSPy 希望分数越大越好，因此返回负的 loss
        return -float(loss_value)

    return dspy_metric
