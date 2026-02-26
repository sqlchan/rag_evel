# ragas/executor.py 功能说明

## 概述
异步任务执行器：提交带索引的协程、按顺序收集结果、支持取消、可选批处理与进度条；供 evaluation 按行按指标提交 score 任务。

## Executor
- **submit(callable, *args, name, **kwargs)**: 用 wrap_callable_with_index 包装为返回 (counter, result) 的 async，异常时根据 raise_exceptions 抛出或返回 (counter, np.nan)，并递增 _jobs_processed。
- **cancel() / is_cancelled()**: 通过 _cancel_event 发出/检测取消。
- **_process_jobs**: 复制 jobs 后清空原列表；无 batch_size 时单进度条 + _process_coroutines；有 batch_size 时 _process_batched_jobs（嵌套进度条、按批 as_completed、cancel_check）。
- **_process_coroutines**: 将 (afunc, args, kwargs, _) 转为协程列表，process_futures(as_completed(..., cancel_check=self.is_cancelled))，按 raise_exceptions 决定是否把 Exception 结果重新抛出，并更新 pbar。
- **aresults()**: 调用 _process_jobs，按第一维（提交顺序）排序后返回 [r[1]]。
- **results()**: 同步入口：apply_nest_asyncio + run(_async_wrapper) 执行 aresults()。

## run_async_batch
- 创建 Executor（raise_exceptions=True，可选 batch_size），对 kwargs_list 逐条 submit(func, **kwargs)，返回 executor.results()。
