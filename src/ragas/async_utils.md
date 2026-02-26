# ragas/async_utils.py 功能说明

## 概述
异步工具：事件循环检测、nest_asyncio 兼容（如 Jupyter）、协程并发与进度处理。

## 事件循环
- **is_event_loop_running()**: 通过 `asyncio.get_running_loop()` 判断当前是否有运行中的事件循环。
- **apply_nest_asyncio()**: 若已有运行中的循环且非 uvloop，则调用 `nest_asyncio.apply()`，便于在 Jupyter 等环境内嵌套运行 async；与 uvloop 不兼容时返回 False。

## 协程执行
- **as_completed(coroutines, max_workers, cancel_check, cancel_pending)**: 使用可选信号量限制并发数，返回按完成顺序的 Future 迭代器；若提供 cancel_check，可在迭代时取消未完成任务。
- **process_futures(futures)**: 异步迭代 futures，await 每个 future，非 CancelledError 的异常作为结果 yield，便于统一处理错误。

## 运行入口
- **run(async_func, allow_nest_asyncio)**: 执行单个 async 函数或协程；若允许则先 apply_nest_asyncio；在已有循环且未应用 nest_asyncio 时，对 uvloop 抛出明确 RuntimeError。
- **run_async_tasks(tasks, batch_size, show_progress, progress_bar_desc, max_workers, cancel_check)**: 执行一批协程，可选分批与进度条，内部用 ProgressBarManager 与 batched；结果顺序不保证；任一步异常会收集后统一抛出第一个。
