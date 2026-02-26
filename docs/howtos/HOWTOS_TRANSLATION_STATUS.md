# docs/howtos 中英翻译进度

## 规则摘要

- 仅处理 `.md`，不处理已存在的 `*_zh.md`。
- 正文、标题、列表、说明译成简体中文；代码块、命令、URL、文件名、变量/类/函数名保持英文。
- 同目录下链接 `.md` → `_zh.md`；概念等可链向已有 `_zh` 版本。
- 保持 Markdown 结构、代码块、表格、admonitions 不变。

## 已生成 _zh.md 的文件（本次或原有）

| 路径 | 说明 |
|------|------|
| `observability_zh.md` | 已创建 |
| `index_zh.md` | 原有 |
| `llm-adapters_zh.md` | 原有 |
| `applications/index_zh.md` | 原有 |
| `applications/add_to_ci_zh.md` | 已创建 |
| `applications/align-llm-as-judge_zh.md` | 已创建 |
| `applications/benchmark_llm_zh.md` | 已创建 |
| `applications/compare_embeddings_zh.md` | 已创建 |
| `applications/compare_llms_zh.md` | 已创建 |
| `applications/evaluate-and-improve-rag_zh.md` | 已创建 |
| `applications/evaluating_multi_turn_conversations_zh.md` | 已创建（部分为摘要） |
| `applications/_cost_zh.md` | 已创建 |
| `cli/index_zh.md` | 原有 |
| `cli/rag_eval_zh.md` | 已创建 |
| `customizations/index_zh.md` | 原有 |
| `integrations/index_zh.md` | 原有 |

## 尚未翻译的 .md 文件（需生成对应 _zh.md）

### applications/
- `iterate_prompt.md`
- `prompt_optimization.md`
- `singlehop_testset_gen.md`
- `text2sql.md`
- `vertexai_alignment.md`
- `vertexai_model_comparision.md`
- `vertexai_x_ragas.md`

### cli/
- `agent_evals.md`
- `benchmark_llm.md`
- `improve_rag.md`
- `judge_alignment.md`
- `llamaIndex_agent_evals.md`
- `prompt_evals.md`
- `text2sql.md`
- `workflow_eval.md`

### customizations/
- `run_config.md`
- `cancellation.md`
- `customize_models.md`
- `_caching.md`
- `metrics/tracing.md`
- `metrics/_cost.md`
- `metrics/metrics_language_adaptation.md`
- `metrics/modifying-prompts-metrics.md`
- `optimizers/index.md`
- `testgenerator/index.md`
- `testgenerator/prechunked_data.md`
- `testgenerator/_testgen-customisation.md`
- `testgenerator/_testgen-custom-single-hop.md`
- `testgenerator/_language_adaptation.md`
- `testgenerator/_persona_generator.md`

### integrations/
- `ag_ui.md`, `_ag_ui.md`
- `amazon_bedrock.md`
- `gemini.md`
- `griptape.md`
- `haystack.md`, `_haystack.md`
- `langchain.md`, `_langchain.md`
- `langsmith.md`, `_langsmith.md`
- `llama_stack.md`
- `llamaindex_agents.md`, `_llamaindex.md`
- `oci_genai.md`
- `r2r.md`
- `swarm_agent_evaluation.md`
- `_arize.md`, `_athina.md`, `_helicone.md`, `_langfuse.md`, `_langgraph_agent_evaluation.md`, `_openlayer.md`, `_opik.md`, `_tonic-validate.md`, `_zeno.md`

### migrations/
- `migrate_from_v01_to_v02.md`
- `migrate_from_v03_to_v04.md`

---

翻译时可按上表逐文件生成同名 `_zh.md`，并修正文档内相对链接（同目录 .md → _zh.md，概念等用已有 _zh 版本）。
