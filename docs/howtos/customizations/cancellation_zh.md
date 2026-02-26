# 取消长时间运行的任务

在处理大数据集或复杂评估时，部分 Ragas 操作可能耗时较长。取消功能允许你在需要时优雅地终止这些长时间运行的任务，在生产环境中尤为重要。

## 概述

Ragas 对以下操作支持取消：
- **`evaluate()`** - 使用指标对数据集的评估
- **`generate_with_langchain_docs()`** - 从文档生成测试集

取消机制是线程安全的，在可能的情况下会优雅终止并返回部分结果。

## 基本用法

### 可取消的评估

不直接运行评估，而是获取一个支持取消的执行器：

```py
from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset

# 你的数据集和指标
dataset = EvaluationDataset(...)
metrics = [...]

# 获取执行器，而不是立即运行评估
executor = evaluate(
    dataset=dataset,
    metrics=metrics,
    return_executor=True  # 关键参数
)

# 此时可以：
# - 取消：executor.cancel()
# - 检查状态：executor.is_cancelled()
# - 获取结果：executor.results()  # 会阻塞直到完成
```

### 可取消的测试集生成

测试集生成同样可返回执行器以便取消：

```py
from ragas.testset.synthesizers.generate import TestsetGenerator

generator = TestsetGenerator(...)

# 获取可取消的生成执行器
executor = generator.generate_with_langchain_docs(
    documents=documents,
    testset_size=100,
    return_executor=True  # 允许通过 Executor 取消
)

# 使用相同的取消接口
executor.cancel()
```

## 生产环境用法

### 1. 超时模式

超过设定时间后自动取消：

```py
import threading
import time

def evaluate_with_timeout(dataset, metrics, timeout_seconds=300):
    """带自动超时的评估。"""
    executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)
    
    results = None
    exception = None
    
    def run_evaluation():
        nonlocal results, exception
        try:
            results = executor.results()
        except Exception as e:
            exception = e
    
    thread = threading.Thread(target=run_evaluation)
    thread.start()
    
    thread.join(timeout=timeout_seconds)
    
    if thread.is_alive():
        print(f"评估超过 {timeout_seconds}s 超时，正在取消...")
        executor.cancel()
        thread.join(timeout=10)  # 按需设置
        return None, "timeout"
    
    return results, exception

# 使用
results, error = evaluate_with_timeout(dataset, metrics, timeout_seconds=600)
if error == "timeout":
    print("评估因超时被取消")
else:
    print(f"评估完成: {results}")
```

### 2. 信号处理模式（Ctrl+C）

允许用户通过键盘中断取消：

```py
import signal
import sys

def setup_cancellation_handler():
    """在 Ctrl+C 时优雅取消。"""
    executor = None
    
    def signal_handler(signum, frame):
        if executor and not executor.is_cancelled():
            print("\n收到中断信号，正在取消评估...")
            executor.cancel()
            print("已请求取消。等待优雅退出...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    return lambda exec: setattr(signal_handler, 'executor', exec)

# 使用
set_executor = setup_cancellation_handler()

executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)
set_executor(executor)

print("评估运行中... 按 Ctrl+C 可优雅取消")
try:
    results = executor.results()
    print("评估成功完成")
except KeyboardInterrupt:
    print("评估已取消")
```

### 3. Web 应用模式

在 Web 应用中，在请求中止时取消操作：

```py
from flask import Flask, request
import threading
import uuid

app = Flask(__name__)
active_evaluations = {}

@app.route('/evaluate', methods=['POST'])
def start_evaluation():
    eval_id = str(uuid.uuid4())
    
    dataset = get_dataset_from_request(request)
    metrics = get_metrics_from_request(request)
    
    executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)
    active_evaluations[eval_id] = executor
    
    def run_eval():
        try:
            results = executor.results()
            store_results(eval_id, results)
        except Exception as e:
            store_error(eval_id, str(e))
        finally:
            active_evaluations.pop(eval_id, None)
    
    threading.Thread(target=run_eval).start()
    
    return {"evaluation_id": eval_id, "status": "started"}

@app.route('/evaluate/<eval_id>/cancel', methods=['POST'])
def cancel_evaluation(eval_id):
    executor = active_evaluations.get(eval_id)
    if executor:
        executor.cancel()
        return {"status": "cancelled"}
    return {"error": "Evaluation not found"}, 404
```

## 高级用法

### 检查取消状态

```py
executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)

def monitor_evaluation():
    while not executor.is_cancelled():
        print("评估仍在运行...")
        time.sleep(5)
    print("评估已取消")

threading.Thread(target=monitor_evaluation).start()

if some_condition():
    executor.cancel()
```

### 部分结果

执行过程中被取消时，可能得到部分结果：

```py
executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)

try:
    results = executor.results()
    print(f"完成了 {len(results)} 条评估")
except Exception as e:
    if executor.is_cancelled():
        print("评估已取消 - 可能有部分结果")
    else:
        print(f"评估失败: {e}")
```

### 自定义取消逻辑

```py
class EvaluationManager:
    def __init__(self):
        self.executors = []
    
    def start_evaluation(self, dataset, metrics):
        executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)
        self.executors.append(executor)
        return executor
    
    def cancel_all(self):
        """取消所有正在运行的评估。"""
        for executor in self.executors:
            if not executor.is_cancelled():
                executor.cancel()
        print(f"已取消 {len(self.executors)} 个评估")
    
    def cleanup_completed(self):
        """移除已完成的执行器。"""
        self.executors = [ex for ex in self.executors if not ex.is_cancelled()]

# 使用
manager = EvaluationManager()

exec1 = manager.start_evaluation(dataset1, metrics)
exec2 = manager.start_evaluation(dataset2, metrics)

manager.cancel_all()
```

## 最佳实践

### 1. 生产环境务必设置超时
```py
# 推荐：设置合理超时
results, error = evaluate_with_timeout(dataset, metrics, timeout_seconds=1800)  # 30 分钟

# 避免：无限阻塞
results = executor.results()  # 可能一直阻塞
```

### 2. 优雅处理取消
```py
try:
    results = executor.results()
    process_results(results)
except Exception as e:
    if executor.is_cancelled():
        log_cancellation()
        cleanup_partial_work()
    else:
        log_error(e)
        handle_failure()
```

### 3. 给用户反馈
```py
def run_with_progress_and_cancellation(executor):
    print("评估开始... 按 Ctrl+C 取消")
    
    def show_progress():
        while not executor.is_cancelled():
            print(".", end="", flush=True)
            time.sleep(1)
    
    progress_thread = threading.Thread(target=show_progress)
    progress_thread.daemon = True
    progress_thread.start()
    
    try:
        return executor.results()
    except KeyboardInterrupt:
        print("\n正在取消...")
        executor.cancel()
        return None
```

### 4. 释放资源
```py
def managed_evaluation(dataset, metrics):
    executor = None
    try:
        executor = evaluate(dataset=dataset, metrics=metrics, return_executor=True)
        return executor.results()
    except Exception as e:
        if executor:
            executor.cancel()
        raise
    finally:
        cleanup_temp_files()
```

## 限制

- **异步操作**：取消作用于任务级别，不会中断单次 LLM 调用内部
- **部分状态**：取消后可能留下部分结果或临时文件
- **时机**：取消是协作式的，任务需要定期检查取消标志
- **依赖**：部分外部服务可能不会立即响应取消

## 故障排除

### 取消无效
```py
if executor.is_cancelled():
    print("已请求取消")
else:
    print("尚未请求取消")

executor.cancel()
assert executor.is_cancelled()
```

### 取消后任务仍在运行
```py
executor.cancel()
time.sleep(2)  # 留出时间让任务检测取消

# 必要时强制清理
import asyncio
try:
    loop = asyncio.get_running_loop()
    for task in asyncio.all_tasks(loop):
        task.cancel()
except RuntimeError:
    pass  # 无事件循环在运行
```

取消功能为长时间运行的 Ragas 操作提供了可靠控制，便于在生产环境中做好资源管理和用户体验。
