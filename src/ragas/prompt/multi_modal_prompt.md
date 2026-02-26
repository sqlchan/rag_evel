# multi_modal_prompt.py 功能说明

## 概述

`multi_modal_prompt.py` 提供 **图文多模态** 提示词：**ImageTextPrompt** 继承 PydanticPrompt，输入模型可包含文本与图片引用；**ImageTextPromptValue** 将 prompt 项转换为 LangChain 的 **HumanMessage**，其中每项可以是文本或图片（Base64 data URI、允许的 HTTP(S) URL，或可选的本地文件）。包含严格的 **SSRF 与本地路径安全策略**（IP 检查、大小与类型校验等）。

## 主要组件

### 1. ImageTextPrompt(PydanticPrompt)

- **_generate_examples()**：若有 examples，格式化为 “仅文本语境下的示例，但若提供图片请使用” + 每条 input/output 的 JSON；无示例则返回空串。
- **to_prompt_value(data)**：将 instruction、output signature、examples 与 “Now perform…” 以及 **data.to_string_list()**（输入模型需实现该方法，返回文本与图片引用的列表）拼成 **ImageTextPromptValue(items=...)**。
- **generate_multiple**：process_input → 建 callback 组 → to_prompt_value(processed_data)；根据 llm 类型调用 LangChain 的 agenerate_prompt 或 Ragas 的 generate；对每条输出用 RagasOutputParser 或 model_validate_json 解析，process_output 后返回。

### 2. ImageTextPromptValue(PromptValue)

- **items**：字符串列表，每一项可以是：纯文本、Base64 图片 data URI、HTTP(S) 图片 URL，或（在开启本地文件时）允许的本地路径。
- **to_messages()**：遍历 items，对每项调用 **_securely_process_item**，得到 content 列表（text / image_url），过滤 None 后组装成一条 **HumanMessage(content=...)**。
- **_securely_process_item(item)**：按顺序尝试：
  1. **Base64 data URI**（_try_process_base64_uri）：符合 `data:image/(png|jpeg|gif|webp);base64,...` 则解码校验后返回 image payload；
  2. **允许的 URL**（_try_process_allowed_url）：scheme 为 http/https 则 _download_validate_and_encode（含 SSRF 检查、大小、Pillow 校验），返回 image payload；
  3. **本地文件**（仅当 ALLOW_LOCAL_FILE_ACCESS 且 _looks_like_image_path）：_try_process_local_file，在 ALLOWED_IMAGE_BASE_DIR 下解析路径、防遍历、校验大小与图片格式；
  4. 否则视为 **纯文本**（_get_text_payload）。
- **_get_text_payload / _get_image_payload**：返回符合 TypedDict 的 text 或 image_url content。
- **to_string()**：将 items 用空格拼接成单字符串（用于日志或非多模态回退）。

### 3. 安全相关常量与逻辑

- **ALLOWED_URL_SCHEMES**：仅 http、https。
- **MAX_DOWNLOAD_SIZE_BYTES / REQUESTS_TIMEOUT_SECONDS**：下载大小与超时。
- **DATA_URI_REGEX**：匹配标准图片 base64 data URI。
- **ALLOW_LOCAL_FILE_ACCESS / ALLOWED_IMAGE_BASE_DIR**：默认关闭本地文件；若开启则仅允许指定目录下、且经路径规范化与遍历检查的路径。
- **_download_validate_and_encode**：先 **_is_safe_url_target**（解析 hostname，禁止 loopback/private/link_local/reserved）；再 requests.get stream、检查 Content-Length、流式累计大小、Pillow 校验并 base64 编码。
- **_try_process_local_file**：仅在 ALLOW_LOCAL_FILE_ACCESS 且 ALLOWED_IMAGE_BASE_DIR 有效时执行；防绝对路径与 `..`、commonprefix 防遍历、文件存在与大小检查、Pillow 校验后编码。

## 使用场景

- 多模态评估或生成任务：输入除文本外还有图片（截图、图表等），需要传给支持 vision 的 LLM。
- 图片来源为 URL 或 Base64 时可直接使用；本地文件需显式开启并配置白名单目录，以兼顾安全。
