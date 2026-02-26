=== "OpenAI"
    安装 langchain-openai 包

    ```bash
    pip install langchain-openai
    ```

    确保已将 OpenAI 密钥准备好并设置在环境变量中

    ```python
    import os
    os.environ["OPENAI_API_KEY"] = "your-openai-key"
    ```

    使用 `LangchainLLMWrapper` 包装 LLM，以便在 ragas 中使用。

    ```python
    from ragas.llms import LangchainLLMWrapper
    from langchain_openai import ChatOpenAI
    from ragas.embeddings import OpenAIEmbeddings
    import openai
    
    generator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))
    openai_client = openai.OpenAI()
    generator_embeddings = OpenAIEmbeddings(client=openai_client)
    ```


=== "AWS"
    安装 langchain-aws 包

    ```bash
    pip install langchain-aws
    ```

    然后需要设置 AWS 凭据和配置

    ```python
    config = {
        "credentials_profile_name": "your-profile-name",  # 例如 "default"
        "region_name": "your-region-name",  # 例如 "us-east-1"
        "llm": "your-llm-model-id",  # 例如 "anthropic.claude-3-5-sonnet-20241022-v2:0"
        "embeddings": "your-embedding-model-id",  # 例如 "amazon.titan-embed-text-v2:0"
        "temperature": 0.4,
    }
    ```

    定义 LLM 并使用 `LangchainLLMWrapper` 包装，以便在 ragas 中使用。

    ```python
    from langchain_aws import ChatBedrockConverse
    from langchain_aws import BedrockEmbeddings
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper

    generator_llm = LangchainLLMWrapper(ChatBedrockConverse(
        credentials_profile_name=config["credentials_profile_name"],
        region_name=config["region_name"],
        base_url=f"https://bedrock-runtime.{config['region_name']}.amazonaws.com",
        model=config["llm"],
        temperature=config["temperature"],
    ))
    generator_embeddings = LangchainEmbeddingsWrapper(BedrockEmbeddings(
        credentials_profile_name=config["credentials_profile_name"],
        region_name=config["region_name"],
        model_id=config["embeddings"],
    ))
    ```

    如需了解更多关于使用其他 AWS 服务的信息，请参阅 [langchain-aws](https://python.langchain.com/docs/integrations/providers/aws/) 文档。

=== "Google Cloud"
    Google 提供两种访问其模型的方式：Google AI 和 Google Cloud Vertex AI。Google AI 仅需 Google 账号和 API 密钥，而 Vertex AI 需要具备企业功能的 Google Cloud 账号。

    首先安装所需包：

    ```bash
    pip install langchain-google-genai langchain-google-vertexai
    ```

    然后根据所选的 API 设置凭据：

    Google AI：

    ```python
    import os
    os.environ["GOOGLE_API_KEY"] = "your-google-ai-key"  # 来自 https://ai.google.dev/
    ```

    Vertex AI：

    ```python
    # 确保已配置凭据（gcloud、工作负载身份等）
    # 或设置服务账号 JSON 路径：
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/service-account.json"
    ```

    定义配置：

    ```python
    config = {
        "model": "gemini-1.5-pro",  # 或其他模型 ID
        "temperature": 0.4,
        "max_tokens": None,
        "top_p": 0.8,
        # 仅 Vertex AI：
        "project": "your-project-id",  # Vertex AI 必填
        "location": "us-central1",     # Vertex AI 必填
    }
    ```

    初始化 LLM 并包装以供 ragas 使用：

    ```python
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper

    # 根据所用 API 选择对应导入：
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_google_vertexai import ChatVertexAI

    # 使用 Google AI Studio 初始化
    generator_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(
        model=config["model"],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        top_p=config["top_p"],
    ))

    # 或使用 Vertex AI 初始化
    generator_llm = LangchainLLMWrapper(ChatVertexAI(
        model=config["model"],
        temperature=config["temperature"],
        max_tokens=config["max_tokens"],
        top_p=config["top_p"],
        project=config["project"],
        location=config["location"],
    ))
    ```


    可选配置安全设置：

    ```python
    from langchain_google_genai import HarmCategory, HarmBlockThreshold

    safety_settings = {
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        # 按需添加其他安全设置
    }

    # 在 LLM 初始化时应用
    generator_llm = LangchainLLMWrapper(ChatGoogleGenerativeAI(
        model=config["model"],
        temperature=config["temperature"],
        safety_settings=safety_settings,
    ))
    ```

    初始化嵌入模型并包装以供 ragas 使用：

    ```python
    # Google AI Studio 嵌入
    from langchain_google_genai import GoogleGenerativeAIEmbeddings

    generator_embeddings = LangchainEmbeddingsWrapper(GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",  # Google 文本嵌入模型
        task_type="retrieval_document"  # 可选：指定任务类型
    ))
    ```

    ```python
    # Vertex AI 嵌入
    from langchain_google_vertexai import VertexAIEmbeddings

    generator_embeddings = LangchainEmbeddingsWrapper(VertexAIEmbeddings(
        model_name="textembedding-gecko@001",  # 或其他可用模型
        project=config["project"],  # 你的 GCP 项目 ID
        location=config["location"]  # 你的 GCP 区域
    ))
    ```

    有关可用模型、功能和配置的更多信息，请参阅：[Google AI 文档](https://ai.google.dev/docs)、[Vertex AI 文档](https://cloud.google.com/vertex-ai/docs)、[LangChain Google AI 集成](https://python.langchain.com/docs/integrations/chat/google_generative_ai)、[LangChain Vertex AI 集成](https://python.langchain.com/docs/integrations/chat/google_vertex_ai)


=== "Azure"
    安装 langchain-openai 包

    ```bash
    pip install langchain-openai
    ```

    确保已将 Azure OpenAI 密钥准备好并设置在环境变量中。

    ```python
    import os
    os.environ["AZURE_OPENAI_API_KEY"] = "your-azure-openai-key"

    # 其他配置
    azure_config = {
        "base_url": "",  # 你的端点
        "model_deployment": "",  # 你的模型部署名称
        "model_name": "",  # 你的模型名称
        "embedding_deployment": "",  # 你的嵌入部署名称
        "embedding_name": "",  # 你的嵌入名称
    }

    ```

    定义 LLM 并使用 `LangchainLLMWrapper` 包装，以便在 ragas 中使用。

    ```python
    from langchain_openai import AzureChatOpenAI
    from langchain_openai import AzureOpenAIEmbeddings
    from ragas.llms import LangchainLLMWrapper
    from ragas.embeddings import LangchainEmbeddingsWrapper
    generator_llm = LangchainLLMWrapper(AzureChatOpenAI(
        openai_api_version="2023-05-15",
        azure_endpoint=azure_configs["base_url"],
        azure_deployment=azure_configs["model_deployment"],
        model=azure_configs["model_name"],
        validate_base_url=False,
    ))

    # 为 answer_relevancy、answer_correctness 和 answer_similarity 初始化嵌入
    generator_embeddings = LangchainEmbeddingsWrapper(AzureOpenAIEmbeddings(
        openai_api_version="2023-05-15",
        azure_endpoint=azure_configs["base_url"],
        azure_deployment=azure_configs["embedding_deployment"],
        model=azure_configs["embedding_name"],
    ))
    ```

    如需了解更多关于使用其他 Azure 服务的信息，请参阅 [langchain-azure](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/) 文档。

=== "其他"
    若使用其他 LLM 提供商并通过 LangChain 与其交互，可使用 `LangchainLLMWrapper` 包装你的 LLM，以便在 ragas 中使用。

    ```python
    from ragas.llms import LangchainLLMWrapper
    generator_llm = LangchainLLMWrapper(your_llm_instance)
    ```

    更详细说明请参阅[自定义模型指南](../../howtos/customizations/customize_models.md)。

    若使用 LlamaIndex，可使用 `LlamaIndexLLMWrapper` 包装你的 LLM，以便在 ragas 中使用。

    ```python
    from ragas.llms import LlamaIndexLLMWrapper
    generator_llm = LlamaIndexLLMWrapper(your_llm_instance)
    ```

    有关 LlamaIndex 的更多信息，请参阅 [LlamaIndex 集成指南](./../../howtos/integrations/_llamaindex.md)。

    若仍无法在 Ragas 中使用你喜欢的 LLM 提供商，请在此 [issue](https://github.com/vibrantlabsai/ragas/issues/1617) 下留言，我们会为其添加支持 🙂。
