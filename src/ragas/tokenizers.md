# ragas/tokenizers.py 功能说明

## 概述
分词器抽象与两种实现：Tiktoken（OpenAI）与 HuggingFace；懒加载默认实例与工厂函数。

## BaseTokenizer（抽象类）
- **encode(text) -> List[int]**、**decode(tokens) -> str**；**count_tokens(text)** 默认 len(encode(text))。

## TiktokenWrapper
- 构造可传 encoding、model_name 或 encoding_name；默认 "o200k_base"。encode 使用 disallowed_special=()；暴露 **encoding** 属性。

## HuggingFaceTokenizer
- 构造需 tokenizer 或 model_name（用 AutoTokenizer.from_pretrained）；encode 使用 add_special_tokens=False，decode 使用 skip_special_tokens=True；暴露 **tokenizer** 属性。

## 默认与懒加载
- **get_default_tokenizer()**: 全局单例 TiktokenWrapper("o200k_base")，首次访问时创建。
- **_LazyTokenizer**: 继承 BaseTokenizer，__getattr__/encode/decode/count_tokens 均委托 get_default_tokenizer()，避免 import 时网络调用。
- **DEFAULT_TOKENIZER**: _LazyTokenizer() 实例。

## get_tokenizer
- tokenizer_type 为 "tiktoken" 时返回 TiktokenWrapper(model_name, encoding_name)；为 "huggingface" 时要求 model_name，返回 HuggingFaceTokenizer；否则 ValueError。
