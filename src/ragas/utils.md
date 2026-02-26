# ragas/utils.py 功能说明

## 概述
通用工具：缓存与调试、数值/数组处理、数据集列名映射、分词计数、进度条、日志、命名与 Git/ID 等。

## 环境与缓存
- **get_cache_dir()**: XDG_CACHE_HOME 或 ~/.cache，子目录 ragas；可被 RAGAS_CACHE_HOME 覆盖。
- **get_debug_mode()**: 读取 RAGAS_DEBUG 环境变量。

## 数值与校验
- **safe_nanmean(arr)**: 空或全 NaN 返回 np.nan，否则 np.nanmean。
- **check_if_sum_is_close(values, close_to, num_places)**: 按位数舍入后比较和。
- **is_nan(x)**: 安全判断 NaN（非数值类型返回 False）。

## 指标与弃用
- **get_metric_language(metric)**: 从 metric 的 BasePrompt 属性取 language。
- **DeprecationHelper**: 包装类，调用或访问属性时发出弃用警告并转发到 new_target。
- **deprecated(since, removal, alternative, addendum, pending)**: 装饰器，发出 DeprecationWarning。

## 字典与列名
- **get_or_init(dictionary, key, default)**: 无值时用 default() 并等效写入。
- **get_from_dict(data_dict, key, default)**: 支持 "a.b.c" 形式的嵌套键。
- **REQUIRED_COLS_v1**: user_input->question 等映射；**convert_row_v1_to_v2**、**convert_v1_to_v2_dataset**、**convert_v2_to_v1_dataset**：v1/v2 列名互转。

## 分词与批处理
- **num_tokens_from_string(string, encoding_name, tokenizer)**: 用 tokenizer 或 tiktoken 计 token 数。
- **batched(iterable, n)**: 按 n 分批的迭代器。

## 进度与日志
- **ProgressBarManager**: create_single_bar、create_nested_bars、update_batch_bar；根据 show_progress 控制 tqdm 是否禁用。
- **set_logging_level**、**_ContextualFormatter**: 带 UTC/本地时间、ragas_id、app_version 的日志格式。
- **console**: Rich Console 单例。

## 命名与路径
- **MemorableNames**: 形容词+科学家名生成可读名称；generate_unique_name 避免重复，必要时加数字后缀。
- **find_git_root(start_path)**: 向上查找 .git 目录。
- **create_nano_id(size)**: 基于 UUID 的短字母数字 ID。
- **get_test_directory()**: 临时目录 ragas_test_{nano_id}，进程内使用。

## 异步
- **async_to_sync(async_func)**: 若已在事件循环中则用 ThreadPoolExecutor 跑 asyncio.run；否则直接 asyncio.run。
