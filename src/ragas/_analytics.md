# ragas/_analytics.py 功能说明

## 概述
匿名使用统计与事件上报模块，用于了解 Ragas 使用情况；支持关闭追踪与调试模式。

## 关键常量
- **USAGE_TRACKING_URL**: 上报端点（legacy 保留 explodinggradients.com）
- **RAGAS_DO_NOT_TRACK**: 环境变量，设为 `true` 关闭追踪
- **RAGAS_DEBUG_TRACKING**: 开发调试用，打印事件 payload

## 核心逻辑

### 开关与静默
- **do_not_track()**: 根据环境变量判断是否禁用追踪（带 lru_cache）
- **silent**: 装饰器，追踪逻辑内异常静默处理，调试模式下可打印或重新抛出

### 用户标识
- **get_userid()**: 从 `appdirs` 用户目录下的 `uuid.json` 读取或生成 `a-{uuid}`，失败时返回 `anonymous-{uuid}`

### 事件模型（Pydantic）
- **BaseEvent**: event_type, user_id, ragas_version
- **EvaluationEvent**: 评估事件（metrics、num_rows、evaluation_type、language）
- **TestsetGenerationEvent**: 测试集生成事件
- **IsCompleteEvent**, **LLMUsageEvent**, **EmbeddingUsageEvent**, **PromptUsageEvent**: 各类使用/完成事件

### 批处理与上报
- **AnalyticsBatcher**: 后台线程按 batch_size 或 flush_interval 将事件合并（同类型合并 num_rows）后调用 **track()** 发送
- **track()**: 若未禁用则 POST 到 USAGE_TRACKING_URL；调试模式下只打日志不发送
- **track_was_completed**: 装饰器，在函数执行前后发送开始/完成事件

## 进程退出
通过 `atexit.register(_analytics_batcher.shutdown)` 在退出时停止后台线程并做最后一次 flush。
