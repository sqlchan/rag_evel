# ragas/cache.py 功能说明

## 概述
为函数结果提供可插拔的缓存层：抽象接口、磁盘后端、基于参数哈希的 key 生成，以及兼容 instructor 的 Pydantic 序列化。

## 接口与实现
- **CacheInterface**: 抽象基类，定义 get(key)、set(key, value)、has_key(key)；并实现 **__get_pydantic_core_schema__** 供 Pydantic 校验。
- **DiskCacheBackend**: 使用 diskcache.Cache(cache_dir)，实现上述接口；析构时 close；需安装 diskcache。

## 缓存 key
- **_make_hashable(o)**: 将 list/tuple/dict/set/BaseModel 转为可哈希元组，用于参与 key 计算。
- **EXCLUDE_KEYS**: 如 "callbacks" 不参与 key，避免不可哈希或无关变更导致 cache 失效。
- **_generate_cache_key(func, args, kwargs)**: 用函数限定名与哈希化后的 args/kwargs 做 JSON 再 SHA256，得到缓存 key。

## 可序列化处理
- **_make_pydantic_picklable(obj)**: 针对 instructor 动态子类导致的「类身份不一致」问题，从模块中取同名类并用 model_dump 重建实例，使缓存可正确序列化/反序列化。

## 装饰器
- **cacher(cache_backend)**: 装饰器；若 backend 为 None 则直接返回原函数。对 sync/async 分别实现 wrapper：先查 key，命中则返回缓存值；未命中则执行函数，对返回值做 _make_pydantic_picklable 后写入缓存并返回原结果。
