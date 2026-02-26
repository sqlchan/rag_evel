# 评估多轮对话

本教程受 Hamel 关于评估基于 LLM 应用的多轮对话的笔记启发，目标是使用 Ragas 指标建立简单、可操作的评估框架，明确定义何为成功的对话。学完后，你将能基于对 AI 应用的错误分析进行多轮评估。

### Ragas 指标

Ragas 提供 **AspectCritic**，用于评估多轮对话并给出二值结果的强指标，可判断对话是否满足预定义的成功标准。

**[AspectCritic](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/general_purpose/#aspect-critic)**  
AspectCritic 根据以自然语言自由形式预定义的方面（aspect）评估回答，返回二值结果，表示回答是否符合该方面。

该指标与 Hamel 的[建议](https://hamel.dev/notes/llm/officehours/evalmultiturn.html#focus-on-binary-decisions)一致：聚焦二值决策，减少歧义，便于明确改进对话质量。

### 实践示例：评估银行客服聊天机器人

评估时应选择与用户需求直接对应的指标，分数变化应反映对用户体验的真实影响。

假设你在为一家银行构建聊天机器人。

经过[错误分析](https://hamel.dev/notes/llm/officehours/erroranalysis.html#the-data-first-approach)后发现，聊天机器人有时会忘记用户要求完成的任务，或只完成一部分。为改进表现，需要可靠地**量化和评估**这类行为。

> **说明**：定义评分标准时请使用统一术语。  
> - 用户消息称为 `human` message。  
> - 聊天机器人消息称为 `AI` message。

（代码块与原文一致，此处省略重复代码。）

使用 LLM 指标评估时，每个指标可能涉及一次或多次 LLM 调用。评估的 trace 有助于理解结果和排查问题。更多细节见[此页](https://docs.ragas.io/en/stable/howtos/applications/_metrics_llm_calls/)。

错误分析中还可发现另一种模式：银行聊天机器人有时会从基础账户服务偏离到未经授权的投资建议。为维护用户信任并满足监管要求，你希望系统在对话接近这些边界时实现**得体过渡**。可以通过定义如下指标来实现：

（代码块与原文一致。）

### 语气（Tonality）

本节探讨如何评估聊天机器人在不同地区和文化下是否保持一致的语气——这是多语言部署中最具挑战的方面之一。

在一种文化中得体的表达，在另一种文化中可能被不同理解。例如，在日本礼貌常表现为正式、间接、尊重，而在墨西哥则多为热情、友好、有互动感。

为确保聊天机器人适应这些文化差异，可以定义自定义评估指标，判断语气是否符合各目标受众的预期。

（代码块与原文一致。）

上述评估结果说明，在墨西哥被认为礼貌的表达在日本可能不被视为礼貌。

### 品牌语气检查

本节探讨如何评估聊天机器人的语气是否与企业的价值观、目标受众和整体品牌形象一致。

**什么是品牌语气（Brand Tone of Voice）？**  
品牌语气指品牌在与受众进行书面或口头沟通时的用词选择。通过定义独特的语气，品牌可以形成真实的人格、风格和态度。  
[参考](https://filestage.io/blog/brand-tone-of-voice-examples/)

例如：

**Google——信息型、有帮助的品牌声音**  
使用 Google 产品时，你是否感觉一切简单直观？一旦切换到其他工具，往往会觉得更复杂。这种顺畅体验来自 Google 对品牌声音的把握。

Google 在保持用户沟通清晰简洁的同时，维持友好、易接近的语气。其品牌声音围绕“有帮助、清晰、易用”，让产品对每个人都直观。  
[参考](https://filestage.io/blog/brand-tone-of-voice-examples/)

可以定义如下自定义评估指标，判断聊天机器人的回答是否符合你的品牌形象：

（代码块与原文一致。）
