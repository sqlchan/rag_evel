# ragas/exceptions.py 功能说明

## 概述
Ragas 异常层次：通用基类、执行器异常、解析/LLM 异常，以及从 experimental 迁移的资源与重复类错误。

## 基类
- **RagasException**: 接收 message，并调用 super().__init__(message)。

## 执行与解析
- **ExceptionInRunner**: 执行器线程内发生异常时抛出，提示查看 traceback 或使用 raise_exceptions=False。
- **RagasOutputParserException**: 输出解析失败（含重试后仍失败）。
- **LLMDidNotFinishException**: LLM 未完成生成，建议增加 max_tokens。

## 通用错误（RagasError 子类）
- **ValidationError**: 字段校验失败。
- **DuplicateError**: 重复资源。
- **NotFoundError** -> **ResourceNotFoundError** -> **ProjectNotFoundError** / **DatasetNotFoundError** / **ExperimentNotFoundError**: 资源不存在。
- **DuplicateResourceError** -> **DuplicateProjectError** / **DuplicateDatasetError** / **DuplicateExperimentError**: 同标识多份资源。
