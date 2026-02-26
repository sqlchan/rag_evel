# ragas/dataset.py 功能说明

## 概述
泛型数据表 DataTable 与具体数据集 Dataset：支持多种后端（实例或字符串注册名）、Pydantic 校验、类 list 接口与持久化。

## DataTable
- **构造**: name, backend（BaseBackend 或字符串）, data_model（可选）, data（可选列表）。backend 为字符串时通过 **_resolve_backend** 从 get_registry() 解析并传入 **kwargs 构造。
- **load(cls, name, backend, data_model, **kwargs)**: 类方法。根据 DATATABLE_TYPE 调用 backend.load_dataset 或 load_experiment；有 data_model 时把 dict 转成模型实例。
- **from_pandas(cls, dataframe, name, backend, data_model, **kwargs)**: 从 DataFrame.to_dict(orient="records") 得到 list，再按 data_model 校验并构造。
- **save()**: 将 _data 转为 dict 列表（BaseModel 用 model_dump），按 DATATABLE_TYPE 调用 backend.save_dataset 或 save_experiment。
- **reload()**: 从后端重新加载并写回 _data，同样按类型做模型校验。
- **validate_with(data_model)**: 仅对「当前无 data_model 且元素为 dict」的数据集做校验，返回新实例。
- **to_pandas()**: 转成 DataFrame。
- **append(item)**: 有 data_model 时校验 dict 或同类型 BaseModel；无 data_model 时仅接受 dict。
- **get_row_value(row, key)**: 兼容 dict 与 BaseModel 的取值。
- **train_test_split(test_size, random_state)**: 打乱后按比例切分，用 InMemoryBackend 存两份 DataTable 并 save，返回 (train, test)。

## Dataset
- 子类 DataTable，**DATATABLE_TYPE = "Dataset"**，用于表示「数据集」而非实验结果的表。
