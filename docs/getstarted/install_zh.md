# 安装

要开始使用，请通过以下命令使用 `pip` 安装 Ragas：

```bash
pip install ragas
```

若要体验最新功能，可从主分支安装最新版本：

```bash
pip install git+https://github.com/vibrantlabsai/ragas.git
```

若计划参与贡献或修改代码，请克隆仓库并设置为 [可编辑安装](https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs)。

```bash
git clone https://github.com/vibrantlabsai/ragas.git 
pip install -e .
```

!!! note "关于 LangChain OpenAI 依赖版本"
    若使用 `langchain_openai`（例如 `ChatOpenAI`），请显式安装 `langchain-core` 和 `langchain-openai` 以避免版本冲突。可根据环境调整版本范围，但显式安装两者有助于避免严格的依赖冲突。
    ```bash
    pip install -U "langchain-core>=0.2,<0.3" "langchain-openai>=0.1,<0.2" openai
    ```
