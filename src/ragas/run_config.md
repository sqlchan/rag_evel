# ragas/run_config.py 功能说明

## 概述
单次运行的超时、重试、并发与随机种子配置；以及基于 tenacity 的同步/异步重试装饰器。

## RunConfig（dataclass）
- **timeout**: 单次操作超时（秒），默认 180。
- **max_retries**: 最大重试次数，默认 10。
- **max_wait**: 重试间最大等待（秒），默认 60。
- **max_workers**: 最大并发数，默认 16。
- **exception_types**: 要重试的异常类型，默认 (Exception,)。
- **log_tenacity**: 是否用 tenacity 打重试日志，默认 False。
- **seed**: 随机种子，默认 42；**__post_init__** 中设置 **rng** = np.random.default_rng(seed=seed)。

## add_retry / add_async_retry
- 使用 tenacity 的 Retrying / AsyncRetrying：wait_random_exponential(multiplier=1, max=max_wait)、stop_after_attempt(max_retries)、retry_if_exception_type(exception_types)、reraise=True；log_tenacity 为真时 after_log 绑定到 ragas.retry.{fn.__name__}。返回 r.wraps(fn)。
