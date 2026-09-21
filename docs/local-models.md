# 本地模型与用途

以下记录用于说明 RTX 5060 Laptop 8GB 上实际使用过的模型，以及它们在本地实验中的用途。

## 当前主要模型

### Qwen/Qwen3-1.7B

当前最常用的 dense LLM。

- dtype：BF16；
- 用途：vLLM inference、runtime tracing、KV / state 相关实验；
- 本地 8 GB VRAM 环境可运行；
- 也是当前 smoke test 的默认模型。

## Multimodal

### Qwen/Qwen3-VL-2B-Instruct

用于本地 VLM / multimodal inference 实验。

主要用途包括：

- visual encoder load；
- multimodal runtime path；
- native vision execution；
- CUDA Graph / execution-path 相关验证。

## Qwen3.5

### Qwen3.5-0.8B

用于早期 hybrid-model runtime / gate 实验。

### Qwen3.5-2B

用于本地 Qwen3.5 inference 与 runtime 实验。

Qwen3.5 系列用于观察与纯 dense Transformer 不同的 runtime path 和 state behavior。

## 早期模型

### Qwen2.5-1.5B-Instruct

早期 vLLM 本地推理实验使用的模型之一，用于验证小显存环境下的基本 serving path。

### Qwen2.5-3B

进行过本地校准尝试。

在部分配置下受到 8 GB VRAM 限制出现 OOM，因此不把它列为当前稳定运行的主模型。

## 使用原则

本地 RTX 5060 主要用于：

- 模型是否能够正常加载；
- runtime path 是否能够复现；
- 小规模 profiling；
- instrumentation；
- cheap falsification；
- mechanism-level debugging。

需要大模型、高 concurrency 或多 GPU 的实验不以这台 8 GB Laptop GPU 作为最终性能评估平台。
