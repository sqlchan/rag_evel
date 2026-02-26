# 传统 NLP 指标

## 非 LLM 字符串相似度

`NonLLMStringSimilarity` 使用传统字符串距离（Levenshtein、Hamming、Jaro 等）衡量 reference 与 response 的相似度，分数 0–1，1 为完全匹配。无需 LLM。可通过 `DistanceMeasure` 选择：`LEVENSHTEIN`（默认）、`HAMMING`、`JARO`、`JARO_WINKLER`。详见 [traditional.md](traditional.md)。

## BLEU 分数

`BleuScore` 通过 n-gram 精确率与简短惩罚比较 response 与 reference，0–1，1 为完全匹配。非 LLM。可经 `kwargs` 传入底层 `sacrebleu.corpus_bleu` 的参数。详见 [traditional.md](traditional.md)。

## ROUGE 分数

`RougeScore` 基于 n-gram 召回、精确率与 F1 衡量 response 与 reference 的重叠，0–1。可配置 `rouge_type`（如 rouge1、rougeL）和 `mode`（precision、recall、fmeasure）。详见 [traditional.md](traditional.md)。

## 精确匹配（Exact Match）

`ExactMatch` 检查 response 与 reference 是否逐字相同。完全一致为 1，否则为 0。适用于工具调用参数等需严格一致的场景。详见 [traditional.md](traditional.md)。

## 字符串包含（String Presence）

`StringPresence` 检查 response 是否包含 reference 文本。包含为 1，否则为 0。适用于关键词/短语必须出现的情形。详见 [traditional.md](traditional.md)。

## CHRF 分数

`CHRFScore` 使用**字符 n-gram F-score** 衡量 response 与 reference 的相似度，兼顾精确率与召回，适用于形态丰富语言或含改写的回答。0–1，非 LLM。可经 `kwargs` 配置 `char_order`、`word_order`、`beta` 等。详见 [traditional.md](traditional.md)。
