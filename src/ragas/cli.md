# ragas/cli.py 功能说明

## 概述
Ragas 命令行入口：评估运行、结果展示、quickstart 模板与 hello_world 示例；基于 Typer + Rich。

## 通用展示
- **success / error / info / warning**: 向 Rich console 输出不同颜色的短消息。
- **create_numerical_metrics_table**: 数值指标表（当前/基线/Delta/门限）。
- **create_categorical_metrics_table**: 分类指标表（类别、当前/基线计数、Delta）。
- **extract_metrics_from_experiment**: 从实验条目中按字段名抽取指标列表。
- **calculate_aggregated_metrics**: 数值求平均、分类求 Counter。
- **separate_metrics_by_type**: 拆成 numeric_metrics 与 categorical_metrics 两个字典。
- **display_metrics_tables**: 分别打印数值表与分类表。

## 评估命令 evals
- **load_eval_module(eval_path)**: 将 eval 文件所在目录加入 sys.path，用 importlib 加载模块。
- **run_experiments**: 通过 project.get_dataset 加载数据集，调用 experiment_func.run_async 跑实验；解析 metrics 列表，聚合当前与基线指标，再按类型展示表格。
- **evals**: 命令入口。加载模块，在模块中查找带 get_dataset/get_experiment 的 project 与带 run_async 的 experiment_func，推断 input_data_class；然后 asyncio.run(run_experiments(...))。

## quickstart
- 无参数时列出模板表（rag_eval、improve_rag、agent_evals 等）。
- 有模板名时：优先从本地 ragas_examples 或仓库 examples 找模板目录；否则从 GitHub 下载 zip 并解压到临时目录，再复制模板。
- 复制时忽略 .venv、__pycache__ 等；创建 evals/datasets、experiments、logs；将原 datasets/contexts 迁到 evals 下；根据模板写 README（improve_rag 与通用两种）；可覆盖已存在目录（需确认）。

## hello_world
- 在指定目录下创建 hello_world/ 及 datasets、experiments；生成 test_data.csv 与 evals.py（含 accuracy_score 指标与 mock_app_endpoint）；提示运行 ragas evals 命令。
