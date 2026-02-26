# 如何估算评估与测试集生成的成本与用量

在使用 LLM 进行评估和测试集生成时，成本是重要因素。Ragas 提供了一些工具来帮助你估算。

## 实现 `TokenUsageParser`

默认情况下，Ragas 不会为 `evaluate()` 计算 token 用量。这是因为 LangChain 的 LLM 并不总是以统一方式返回 token 用量信息。因此要获得用量数据，需要实现 `TokenUsageParser`。

`TokenUsageParser` 是一个函数，用于解析 LangChain 模型 `generate_prompt()` 返回的 `LLMResult` 或 `ChatResult`，并输出 Ragas 期望的 `TokenUsage`。

下面是一个使用我们已定义解析器解析 OpenAI 的示例。


```python
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompt_values import StringPromptValue

gpt4o = ChatOpenAI(model="gpt-4o")
p = StringPromptValue(text="hai there")
llm_result = gpt4o.generate_prompt([p])

# lets import a parser for OpenAI
from ragas.cost import get_token_usage_for_openai

get_token_usage_for_openai(llm_result)
```
Output
```
TokenUsage(input_tokens=9, output_tokens=9, model='')
```


你可以自定义解析器，或使用已定义的解析器。若希望为某 LLM 厂商建议或贡献解析器，请查看此 [issue](https://github.com/vibrantlabsai/ragas/issues/1151) 🙂。

## 评估的 Token 用量

使用 `get_token_usage_for_openai` 解析器计算某次评估的 token 用量。


```python
from ragas import EvaluationDataset
from datasets import load_dataset

dataset = load_dataset("vibrantlabsai/amnesty_qa", "english_v3")

eval_dataset = EvaluationDataset.from_hf_dataset(dataset["eval"])
```
Output
```
Repo card metadata block was not found. Setting CardData to empty.
```

将解析器传入 `evaluate()` 后，成本会被计算并包含在返回的 `Result` 对象中。


```python
from ragas import evaluate
from ragas.metrics import LLMContextRecall

from ragas.cost import get_token_usage_for_openai

result = evaluate(
    eval_dataset,
    metrics=[LLMContextRecall()],
    llm=gpt4o,
    token_usage_parser=get_token_usage_for_openai,
)
```
Output
```
Evaluating:   0%|          | 0/20 [00:00<?, ?it/s]
```


```python
result.total_tokens()
```
Output
```
TokenUsage(input_tokens=25097, output_tokens=3757, model='')
```


可通过向 `Result.total_cost()` 传入每 token 成本来计算每次运行的成本。

本例中 GPT-4o 为每百万输入 token 5 美元、每百万输出 token 15 美元。


```python
result.total_cost(cost_per_input_token=5 / 1e6, cost_per_output_token=15 / 1e6)
```

Output
```
1.1692900000000002
```


## 测试集生成的 Token 用量

测试集生成可使用同一解析器，但需将 `token_usage_parser` 传入 `generate()`。目前仅计算生成过程的成本，不包含 transforms 的成本。

下面示例加载已有 KnowledgeGraph 并生成测试集。若想了解如何生成测试集，请参阅 [测试集生成](../../getstarted/rag_testset_generation_zh.md#a-deeper-look)。


```python
from ragas.testset.graph import KnowledgeGraph

# loading an existing KnowledgeGraph
# make sure to change the path to the location of the KnowledgeGraph file
kg = KnowledgeGraph.load("../../../experiments/scratchpad_kg.json")
kg
```

Output
```
KnowledgeGraph(nodes: 47, relationships: 109)



### Choose your LLM

--8<--
choose_generator_llm.md
--8<--


```python
from ragas.testset import TestsetGenerator
from ragas.llms import llm_factory

tg = TestsetGenerator(llm=llm_factory(), knowledge_graph=kg)
# generating a testset
testset = tg.generate(testset_size=10, token_usage_parser=get_token_usage_for_openai)
```


```python
# total cost for the generation process
testset.total_cost(cost_per_input_token=5 / 1e6, cost_per_output_token=15 / 1e6)
```

Output
```
0.20967000000000002
```
