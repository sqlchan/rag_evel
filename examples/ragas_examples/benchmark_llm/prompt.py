import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

# 加载 .env 中的环境变量（如 OPENAI_API_KEY）
load_dotenv(".env")

# 默认使用的 OpenAI 模型
DEFAULT_MODEL = "gpt-4.1-nano-2025-04-14"


def get_client() -> AsyncOpenAI:
    """懒加载创建 AsyncOpenAI 客户端，仅在真正调用 API 时检查 API Key。

    这样在仅执行 --help 等场景下导入模块不会因缺少 key 而报错。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please export it before running prompts."
        )
    return AsyncOpenAI(api_key=api_key)


# 折扣计算助手的系统提示：定义角色、折扣规则及 JSON 输出格式
SYSTEM_PROMPT = """
You are a discount calculation assistant. I will provide a customer profile and you must calculate their discount percentage and explain your reasoning.

Discount rules:
- Age 65+ OR student status: 15% discount
- Annual income < $30,000: 20% discount  
- Premium member for 2+ years: 10% discount
- New customer (< 6 months): 5% discount

Rules can stack up to a maximum of 35% discount.

Respond in JSON format only:
{
  "discount_percentage": number,
  "reason": "clear explanation of which rules apply and calculations",
  "applied_rules": ["list", "of", "applied", "rule", "names"]
}
"""


async def run_prompt(prompt: str, model: str = DEFAULT_MODEL):
    """使用指定模型运行折扣计算 prompt，返回助手回复的 JSON 文本。"""
    # 按需创建 OpenAI 客户端
    client = get_client()
    # 调用 Chat Completions API：强制 JSON 输出，system + user 消息
    response = await client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    # 取首条回复内容并去除首尾空白
    response = response.choices[0].message.content.strip()
    return response


if __name__ == "__main__":
    import asyncio

    async def main():
        # 示例客户画像：用于本地运行时的演示输入
        customer_profile = """
        Customer Profile:
        - Name: Sarah Johnson
        - Age: 67
        - Student: No
        - Annual Income: $45,000
        - Premium Member: Yes, for 3 years
        - Account Age: 3 years
        """
        print("=== System Prompt ===")
        print(SYSTEM_PROMPT)
        print("\n=== Customer Profile ===")
        print(customer_profile)
        print(f"\n=== Running Prompt with default model {DEFAULT_MODEL} ===")
        print(await run_prompt(customer_profile, model=DEFAULT_MODEL))

    asyncio.run(main())
