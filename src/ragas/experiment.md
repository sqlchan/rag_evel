# ragas/experiment.py 功能说明

## 概述
实验存储（Experiment 继承 DataTable）与实验运行协议：版本化当前代码库、@experiment 装饰器将异步函数包装为可对 Dataset 逐条执行并持久化的实验流程。

## Experiment
- **DATATABLE_TYPE = "Experiment"**，与 Dataset 共用 DataTable 的 load/save/backend 解析，但后端调用 load_experiment/save_experiment。

## version_experiment
- 依赖 GitPython。可选 stage_all 或仅已跟踪文件，commit 后根据 create_branch 创建分支 ragas/{experiment_name}，返回 commit hash；无变更时用当前 HEAD。

## ExperimentProtocol 与 ExperimentWrapper
- **ExperimentProtocol**: 协议类，定义 __call__ 与 arun(dataset, name, backend, *args, **kwargs) -> Experiment。
- **ExperimentWrapper**: 包装用户函数；__call__ 直接调用原函数（支持 async）；**arun**：生成 name（缺省用 memorable_names）、解析 backend（或沿用 dataset.backend）、创建 Experiment 实例，对 dataset 每条 asyncio.create_task 执行 func(item)，as_completed 收集结果并 append，最后 save 并返回 experiment_view。

## experiment 装饰器
- 参数：experiment_model、backend、name_prefix。返回的 decorator 将 func 包成 ExperimentWrapper（传入 experiment_model、default_backend、name_prefix），并 cast 为 ExperimentProtocol。
