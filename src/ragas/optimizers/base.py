import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain_core.callbacks import Callbacks

from ragas.dataset_schema import SingleMetricAnnotation
from ragas.llms.base import BaseRagasLLM
from ragas.losses import Loss
from ragas.metrics.base import MetricWithLLM
from ragas.run_config import RunConfig


@dataclass
class Optimizer(ABC):
    """
    所有优化器的抽象基类。
    Abstract base class for all optimizers.
    """

    # 待优化的指标（须带 LLM，用于评估与生成）
    metric: t.Optional[MetricWithLLM] = None
    # 用于生成/评估的 Ragas LLM
    llm: t.Optional[BaseRagasLLM] = None

    @abstractmethod
    def optimize(
        self,
        dataset: SingleMetricAnnotation,
        loss: Loss,
        config: t.Dict[t.Any, t.Any],
        run_config: t.Optional[RunConfig] = None,
        batch_size: t.Optional[int] = None,
        callbacks: t.Optional[Callbacks] = None,
        with_debugging_logs=False,
        raise_exceptions: bool = True,
    ) -> t.Dict[str, str]:
        """
        Optimizes the prompts for the given metric.

        Parameters
        ----------
        metric : MetricWithLLM
            The metric to optimize.
        train_data : Any
            The training data.
        config : InstructionConfig
            The training configuration.

        Returns
        -------
        Dict[str, str]
            The optimized prompts for given chain.
        """
        raise NotImplementedError("The method `optimize` must be implemented.")
