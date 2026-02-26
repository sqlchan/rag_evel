# benchmark_llm/prompt.py 功能说明

## 概述

本模块是 **Ragas benchmark_llm 示例** 中的提示运行脚本，用于调用 OpenAI 接口执行「折扣计算助手」的 system prompt，根据客户画像计算折扣比例并以 JSON 形式返回结果。可作为 LLM benchmark 或 prompt 迭代的入口。

## 主要功能

1. **环境与客户端**：从 `.env` 加载 `OPENAI_API_KEY`，按需创建 `AsyncOpenAI` 客户端，避免在仅执行 `--help` 等场景下因缺少 key 而报错。
2. **折扣规则与 System Prompt**：内置一套可叠加的折扣规则（年龄/学生、年收入、会员时长、新客等），并定义返回格式为 JSON（`discount_percentage`、`reason`、`applied_rules`）。
3. **异步调用**：提供 `run_prompt(prompt, model)`，使用指定模型和 JSON 模式调用 Chat Completions API，返回助手回复的文本内容。
4. **命令行演示**：`if __name__ == "__main__"` 下使用 asyncio 运行一个示例客户画像（Sarah Johnson），打印 system prompt、客户信息及模型输出，便于本地验证。

## 关键步骤说明

| 步骤 | 说明 |
|------|------|
| `load_dotenv(".env")` | 加载项目根目录下的 `.env`，读取 `OPENAI_API_KEY` 等环境变量。 |
| `get_client()` | 懒加载创建 `AsyncOpenAI`；若未设置 `OPENAI_API_KEY` 则抛出 `RuntimeError`。 |
| `SYSTEM_PROMPT` | 定义折扣规则与 JSON 输出格式，作为每次请求的 system 消息。 |
| `run_prompt(prompt, model)` | 使用 `response_format={"type": "json_object"}` 调用 API，返回 `choices[0].message.content` 的 strip 结果。 |
| `main()` | 构造示例客户画像，依次打印 system prompt、客户信息与模型响应。 |

## 依赖与运行

- **依赖**：`python-dotenv`、`openai`（需在对应环境中安装）。
- **默认模型**：`gpt-4.1-nano-2025-04-14`，可通过 `run_prompt(..., model=...)` 覆盖。
- **运行方式**：在项目根目录或示例目录下执行 `python -m ragas_examples.benchmark_llm.prompt`，需先配置好 `.env` 中的 `OPENAI_API_KEY`。

## 与 benchmark 的关系

该脚本为「单次运行 prompt」的示例；完整的 benchmark 流程（多样本、评估指标、结果汇总）由同目录下的 `evals.py` 等配合数据集 `datasets/discount_benchmark.csv` 完成。
