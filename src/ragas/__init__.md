# ragas/__init__.py 功能说明

## 概述
ragas 包的主入口模块，对外暴露核心 API 与版本信息。

## 主要导出

### 评估与实验
- **evaluate** / **aevaluate**: 对数据集执行评估（同步/异步）
- **Experiment**, **experiment**, **version_experiment**: 实验管理与版本化

### 数据与后端
- **Dataset**, **DataTable**: 数据集与表结构
- **SingleTurnSample**, **MultiTurnSample**, **EvaluationDataset**: 评估样本与数据集 schema
- **backends**: 存储后端注册与实现

### 运行与工具
- **RunConfig**: 超时、重试、并发等运行配置
- **cacher**, **CacheInterface**, **DiskCacheBackend**: 缓存接口与磁盘实现
- **BaseTokenizer**, **TiktokenWrapper**, **HuggingFaceTokenizer**, **get_tokenizer**: 分词器抽象与工厂

### 版本
- **__version__**: 从 `_version` 解析的包版本，解析失败时为 `"unknown version"`

## 懒加载 experimental
通过 `__getattr__("experimental")` 按需导入 `ragas_experimental`，未安装时抛出明确错误，引导用户 `pip install ragas[experimental]`。
