# 自定义超时与速率限制

在使用集合 API 与 `llm_factory` 时，可直接在 LLM 客户端上配置超时与重试。

## OpenAI 客户端配置

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory
from ragas.metrics.collections import Faithfulness

# 在客户端上配置超时与重试
client = AsyncOpenAI(
    timeout=60.0,        # 60 秒超时
    max_retries=5,       # 失败时最多重试 5 次
)

llm = llm_factory("gpt-4o-mini", client=client)

# 与指标一起使用
scorer = Faithfulness(llm=llm)
result = scorer.score(
    user_input="When was the first super bowl?",
    response="The first superbowl was held on Jan 15, 1967",
    retrieved_contexts=[
        "The First AFL–NFL World Championship Game was an American football game played on January 15, 1967, at the Los Angeles Memorial Coliseum in Los Angeles."
    ]
)
```

### 可用参数

| 参数 | 默认值 | 说明 |
|-----------|---------|-------------|
| `timeout` | 600.0 | 请求超时时间（秒） |
| `max_retries` | 2 | 失败请求的重试次数 |

### 细粒度超时控制

若需区分不同类型的超时：

```python
import httpx
from openai import AsyncOpenAI

client = AsyncOpenAI(
    timeout=httpx.Timeout(
        60.0,           # 总超时
        connect=5.0,    # 连接超时
        read=30.0,      # 读超时
        write=10.0,     # 写超时
    ),
    max_retries=3,
)
```

!!! tip "提供商文档"
    各 LLM 提供商有自己的客户端配置选项，请查阅其 SDK 文档：
    
    - [OpenAI Python SDK](https://github.com/openai/openai-python)
    - [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)


## 旧版指标 API

以下示例使用带 `RunConfig` 的旧版指标 API。新项目建议使用上述在客户端层面配置的集合 API。

!!! warning "弃用时间线"
    该 API 将在 0.4 版本弃用，并在 1.0 版本移除。请迁移到基于集合的 API。

### RunConfig 参数

```python
from ragas.run_config import RunConfig

run_config = RunConfig(
    timeout=180,        # 单次操作最大秒数（默认：180）
    max_retries=10,     # 重试次数（默认：10）
    max_wait=60,        # 重试间隔最大秒数（默认：60）
    max_workers=16,     # 并发工作线程数（默认：16）
    log_tenacity=False, # 是否记录重试（默认：False）
    seed=42,            # 随机种子（默认：42）
)
```

### 与 evaluate 一起使用

```python
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import Faithfulness
from ragas.run_config import RunConfig

# 旧版 LLM 配置
llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))

# 配置运行参数
run_config = RunConfig(max_workers=64, timeout=60)

# 与 evaluate 一起使用
results = evaluate(
    dataset=eval_dataset,
    metrics=[Faithfulness(llm=llm)],
    run_config=run_config,
)
```
