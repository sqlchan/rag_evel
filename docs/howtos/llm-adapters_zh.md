# LLM 适配器：使用多种结构化输出后端

Ragas 通过适配器模式支持多种结构化输出后端。本指南说明如何为不同 LLM 提供商使用不同适配器。

## 概述

Ragas 使用适配器处理来自不同 LLM 提供商的结构化输出：

- **Instructor 适配器**：支持 OpenAI、Anthropic、Azure、Groq、Mistral、Cohere 等
- **LiteLLM 适配器**：支持 LiteLLM 所支持的全部 100+ 提供商（Gemini、Ollama、vLLM、Bedrock 等）

框架会自动为你的提供商选择最佳适配器，你也可以显式指定。

## 快速开始

### 自动选择适配器（推荐）

让 Ragas 自动检测最佳适配器：

```python
from ragas.llms import llm_factory
from openai import OpenAI

# OpenAI - 自动使用 Instructor 适配器
client = OpenAI(api_key="...")
llm = llm_factory("gpt-4o-mini", client=client)
```

```python
from ragas.llms import llm_factory
import google.generativeai as genai

# Gemini - 自动使用 LiteLLM 适配器
genai.configure(api_key="...")
client = genai.GenerativeModel("gemini-2.0-flash")
llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
```

### 显式选择适配器

如需更多控制，可指定适配器：

```python
from ragas.llms import llm_factory

# 强制使用 Instructor 适配器
llm = llm_factory("gpt-4o", client=client, adapter="instructor")

# 强制使用 LiteLLM 适配器
llm = llm_factory("gemini-2.0-flash", client=client, adapter="litellm")
```

## 自动检测逻辑

当 `adapter="auto"`（默认）时，Ragas 按以下逻辑选择：

1. **检查 client 类型**：若 client 来自 `litellm` 模块 → 使用 LiteLLM 适配器
2. **检查 provider**：若 provider 为 `google` 或 `gemini` → 使用 LiteLLM 适配器
3. **默认**：其余情况使用 Instructor 适配器

```python
from ragas.llms.adapters import auto_detect_adapter

# 查看将使用的适配器
adapter_name = auto_detect_adapter(client, "google")
print(adapter_name)  # 输出: "litellm"

adapter_name = auto_detect_adapter(client, "openai")
print(adapter_name)  # 输出: "instructor"
```

## 按提供商示例

### OpenAI

```python
from openai import OpenAI
from ragas.llms import llm_factory

client = OpenAI(api_key="your-key")
llm = llm_factory("gpt-4o", client=client)
# 自动使用 Instructor 适配器
```

### Anthropic Claude

```python
from anthropic import Anthropic
from ragas.llms import llm_factory

client = Anthropic(api_key="your-key")
llm = llm_factory("claude-3-sonnet", provider="anthropic", client=client)
# 自动使用 Instructor 适配器
```

### Google Gemini（使用 google-generativeai - 推荐）

```python
import google.generativeai as genai
from ragas.llms import llm_factory

genai.configure(api_key="your-key")
client = genai.GenerativeModel("gemini-2.0-flash")
llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
# 对 google 提供商自动使用 LiteLLM 适配器
```

### Google Gemini（通过 LiteLLM 代理 - 高级）

```python
from openai import OpenAI
from ragas.llms import llm_factory

# 需先运行: litellm --model gemini-2.0-flash
client = OpenAI(
    api_key="anything",
    base_url="http://0.0.0.0:4000"  # LiteLLM 代理端点
)
llm = llm_factory("gemini-2.0-flash", client=client, adapter="litellm")
# 显式使用 LiteLLM 适配器
```

### 本地模型（Ollama）

```python
from openai import OpenAI
from ragas.llms import llm_factory

# Ollama 提供兼容 OpenAI 的 API
client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)
llm = llm_factory("mistral", provider="openai", client=client)
# 使用 Instructor 适配器
```

### AWS Bedrock

```python
from openai import OpenAI
from ragas.llms import llm_factory

# 通过 LiteLLM 代理使用 Bedrock
# 注意：请先配置 LiteLLM 的 Bedrock 凭证
client = OpenAI(
    api_key="",  # Bedrock 使用 IAM 认证
    base_url="http://0.0.0.0:4000"  # LiteLLM 代理端点
)
llm = llm_factory("claude-3-sonnet", client=client, adapter="litellm")
```

### Groq

```python
from groq import Groq
from ragas.llms import llm_factory

client = Groq(api_key="your-key")
llm = llm_factory("mixtral-8x7b", provider="groq", client=client)
# 自动使用 Instructor 适配器
```

### Mistral

```python
from mistralai import Mistral
from ragas.llms import llm_factory

client = Mistral(api_key="your-key")
llm = llm_factory("mistral-large", provider="mistral", client=client)
# 自动使用 Instructor 适配器
```

### Cohere

```python
from cohere import Cohere
from ragas.llms import llm_factory

client = Cohere(api_key="your-key")
llm = llm_factory("command-r-plus", provider="cohere", client=client)
# 自动使用 Instructor 适配器
```

## 适配器选择指南

根据需求选择适配器：

### 在以下情况使用 Instructor 适配器：
- 使用 OpenAI、Anthropic、Azure、Groq、Mistral 或 Cohere
- 提供商被 Instructor 原生支持
- 希望使用最稳定、经过充分测试的方案
- 提供商不需要特殊处理

### 在以下情况使用 LiteLLM 适配器：
- 使用 Google Gemini
- 使用本地模型（Ollama、vLLM 等）
- 使用 100+ 可选提供商（如 Bedrock 等）
- 需要最大程度的提供商兼容性
- 自动检测为你的提供商选择了它

## 直接使用适配器

### 获取可用适配器

```python
from ragas.llms.adapters import ADAPTERS

print(ADAPTERS)
# 输出: {
#     "instructor": InstructorAdapter(),
#     "litellm": LiteLLMAdapter()
# }
```

### 获取指定适配器

```python
from ragas.llms.adapters import get_adapter

instructor = get_adapter("instructor")
litellm = get_adapter("litellm")

# 直接使用适配器创建 LLM
llm = instructor.create_llm(client, "gpt-4o", "openai")
```

## 高级用法

### 模型参数

所有适配器支持相同的模型参数：

```python
llm = llm_factory(
    "gpt-4o",
    client=client,
    temperature=0.7,
    max_tokens=2048,
    top_p=0.9,
)
```

### 系统提示词

两个适配器都支持为需要特定指令的模型设置系统提示词：

```python
llm = llm_factory(
    "gpt-4o",
    client=client,
    system_prompt="You are a helpful assistant that evaluates RAG systems."
)
```

系统提示词适用于：
- LLM 需要特定行为指令时
- 使用带自定义系统提示词的微调模型时
- 希望统一所有指标的评估风格时

系统提示词会作为系统消息附加到所有 LLM 调用之前。

### Instructor 自定义模式

Instructor 适配器支持多种结构化输出生成模式。默认使用 `Mode.JSON`，也可为不支持某些特性的后端指定其他模式：

```python
import instructor
from ragas.llms import llm_factory
from openai import OpenAI

# 对不支持 response_format 的后端使用 MD_JSON 模式
client = OpenAI(api_key="...", base_url="https://custom-backend")
llm = llm_factory(
    "custom-model",
    provider="openai",
    client=client,
    mode=instructor.Mode.MD_JSON
)
```

可用的 instructor 模式：
- `Mode.JSON`（默认）- 使用 OpenAI 的 response_format 参数
- `Mode.MD_JSON` - 在提示词中使用 markdown JSON（用于不支持的后端）
- `Mode.TOOLS` - 使用 function calling
- `Mode.JSON_SCHEMA` - 使用 JSON schema 校验

当遇到类似以下错误时可使用 `Mode.MD_JSON`：
```
Error code: 400 - {'message': 'only pytorch backend can use response_format now'}
```

### 异步支持

两个适配器均支持异步：

```python
from openai import AsyncOpenAI
from ragas.llms import llm_factory

async_client = AsyncOpenAI(api_key="...")
llm = llm_factory("gpt-4o", client=async_client)

# 异步生成
response = await llm.agenerate(prompt, ResponseModel)
```

### 使用 LiteLLM 的自定义提供商

LiteLLM 支持许多 Instructor 未覆盖的提供商。可使用 LiteLLM 代理方式：

```python
from openai import OpenAI
from ragas.llms import llm_factory

# 先启动 LiteLLM 代理:
# litellm --model grok-1  (xAI)
# litellm --model deepseek-chat  (DeepSeek)
# 等

client = OpenAI(
    api_key="your-provider-api-key",
    base_url="http://0.0.0.0:4000"  # LiteLLM 代理端点
)

# xAI Grok
llm = llm_factory("grok-1", client=client, adapter="litellm")

# DeepSeek
llm = llm_factory("deepseek-chat", client=client, adapter="litellm")

# Together AI
llm = llm_factory("mistral-7b", client=client, adapter="litellm")
```

## 完整评估示例

```python
from datasets import Dataset
from ragas import evaluate
from ragas.llms import llm_factory
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    AnswerCorrectness,
)

# 使用你的提供商初始化 LLM
import google.generativeai as genai
genai.configure(api_key="...")
client = genai.GenerativeModel("gemini-2.0-flash")
llm = llm_factory("gemini-2.0-flash", provider="google", client=client)

# 创建评估数据集
data = {
    "question": ["What is the capital of France?"],
    "answer": ["Paris"],
    "contexts": [["France is in Europe. Paris is its capital."]],
    "ground_truth": ["Paris"]
}
dataset = Dataset.from_dict(data)

# 定义指标
metrics = [
    ContextPrecision(llm=llm),
    ContextRecall(llm=llm),
    Faithfulness(llm=llm),
    AnswerCorrectness(llm=llm),
]

# 评估
results = evaluate(dataset, metrics=metrics)
print(results)
```

## 故障排除

### "Unknown adapter: xyz"

确保使用有效的适配器名称：

```python
# 有效: "instructor" 或 "litellm"
llm = llm_factory("model", client=client, adapter="instructor")

# 无效: "dspy"（尚未实现）
# llm = llm_factory("model", client=client, adapter="dspy")  # 报错!
```

### "Failed to initialize provider client"

请确认：
1. client 已正确初始化
2. API 密钥有效
3. 该提供商被适配器支持

```python
# 检查适配器是否能处理你的提供商
from ragas.llms.adapters import auto_detect_adapter
adapter = auto_detect_adapter(client, "my-provider")
print(f"Will use: {adapter}")
```

### 适配器不匹配

自动检测在多数情况下可用，显式选择也有帮助：

```python
# 若自动检测选错了适配器:
llm = llm_factory(
    "model",
    provider="provider-name",
    client=client,
    adapter="litellm"  # 显式覆盖
)
```

## 迁移指南

### 从仅文本到结构化输出

若你从仅文本的 LLM 用法升级：

```python
# 之前（已弃用）
# from ragas.llms import LangchainLLMWrapper
# llm = LangchainLLMWrapper(langchain_llm)

# 之后（新方式）
from ragas.llms import llm_factory
llm = llm_factory("gpt-4o", client=client)
```

### 更换提供商

从 OpenAI 切换到 Gemini：

```python
# 之前: OpenAI
from openai import OpenAI
client = OpenAI(api_key="...")
llm = llm_factory("gpt-4o", client=client)

# 之后: Gemini（代码模式类似！）
import google.generativeai as genai
genai.configure(api_key="...")
client = genai.GenerativeModel("gemini-2.0-flash")
llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
# 对 google 提供商会自动切换为 LiteLLM 适配器
```

## 另见

- [Gemini 集成指南](./integrations/gemini.md) - Gemini 详细配置
- [LLM Factory 参考](./llm-factory.md) - 完整 API 参考
- [指标文档](../concepts/metrics/index.md) - 与 LLM 配合使用指标
