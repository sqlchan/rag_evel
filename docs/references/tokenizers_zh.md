# Tokenizers（分词器）

Ragas 支持多种分词器实现，用于知识图谱操作和测试数据生成时的文本切分。

## 概述

从知识图谱节点提取属性时，会按 token 限制将文本切分为块。默认使用 tiktoken（OpenAI 分词器），也可使用 HuggingFace 分词器以更好地兼容开源模型。

## 可用分词器

### TiktokenWrapper

对 OpenAI tiktoken 分词器的封装，为默认分词器。

```python
from ragas import TiktokenWrapper

# 使用默认编码 (o200k_base)
tokenizer = TiktokenWrapper()

# 使用指定编码
tokenizer = TiktokenWrapper(encoding_name="cl100k_base")

# 使用针对某模型的编码
tokenizer = TiktokenWrapper(model_name="gpt-4")
```

### HuggingFaceTokenizer

对 HuggingFace transformers 分词器的封装，适用于开源模型。

```python
from ragas import HuggingFaceTokenizer

# 加载指定模型的分词器
tokenizer = HuggingFaceTokenizer(model_name="meta-llama/Llama-2-7b-hf")

# 使用已初始化的分词器
from transformers import AutoTokenizer
hf_tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
tokenizer = HuggingFaceTokenizer(tokenizer=hf_tokenizer)
```

**注意：** HuggingFace 分词器需要安装 `transformers` 包：
```sh
pip install transformers
# 或
uv add transformers
```

### 工厂函数

使用 `get_tokenizer()` 可简便地创建分词器：

```python
from ragas import get_tokenizer

# 默认 tiktoken 分词器
tokenizer = get_tokenizer()

# 针对某模型的 tiktoken
tokenizer = get_tokenizer("tiktoken", model_name="gpt-4")

# HuggingFace 分词器
tokenizer = get_tokenizer("huggingface", model_name="meta-llama/Llama-2-7b-hf")
```

## 使用自定义分词器

### 与基于 LLM 的提取器配合

所有基于 LLM 的提取器都接受 `tokenizer` 参数：

```python
from ragas import HuggingFaceTokenizer
from ragas.testset.transforms import (
    SummaryExtractor,
    KeyphrasesExtractor,
    HeadlinesExtractor,
)

# 为你的模型创建 HuggingFace 分词器
tokenizer = HuggingFaceTokenizer(model_name="meta-llama/Llama-2-7b-hf")

# 在提取器中使用
summary_extractor = SummaryExtractor(llm=your_llm, tokenizer=tokenizer)
keyphrase_extractor = KeyphrasesExtractor(llm=your_llm, tokenizer=tokenizer)
headlines_extractor = HeadlinesExtractor(llm=your_llm, tokenizer=tokenizer)
```

### 自定义分词器实现

可通过继承 `BaseTokenizer` 实现自己的分词器：

```python
from ragas.tokenizers import BaseTokenizer

class MyCustomTokenizer(BaseTokenizer):
    def __init__(self, ...):
        # 初始化你的分词器
        pass

    def encode(self, text: str) -> list[int]:
        # 返回 token ID 列表
        pass

    def decode(self, tokens: list[int]) -> str:
        # 返回解码后的文本
        pass
```

## API 参考

::: ragas.tokenizers
