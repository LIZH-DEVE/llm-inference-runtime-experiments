# 模型与架构矩阵

该文档区分完整本地 inference、执行路径验证和源码 / 架构分析，避免把不同验证深度混在一起。

## 完整本地 Inference / Runtime 实验

| 模型 | 架构 | 实验内容 |
| --- | --- | --- |
| **Qwen3-1.7B** | Dense Transformer | BF16 inference、request / scheduler / KV state、runtime tracing |
| **Qwen3.5-2B** | Hybrid | attention 与 recurrent state、state lifetime |
| **Qwen3-VL-2B-Instruct** | Vision-Language Model | visual encoder、multimodal request path、CUDA Graph / eager execution |
| **Qwen2.5-3B-Instruct** | Dense Transformer | serving、chunked prefill、async scheduling、measurement calibration |

## 执行路径 / Kernel 级验证

### Falcon-H1-0.5B

- Hybrid / recurrent architecture；
- 已运行 fast path 与 recurrent kernel；
- 用于观察非纯 attention execution path。

### Qwen3.5-0.8B

- Hybrid architecture；
- 用于低成本检查 recurrent / attention state path。

### Ouro-1.4B

- Looped Transformer；
- 用于 repeated-layer execution、index / metadata reuse 相关实验。

## 源码与架构分析

还阅读或对比过以下模型家族：

- Llama-3
- LLaVA
- Mixtral
- DeepSeek-MoE
- Jamba
- Mamba
- Zamba
- Qwen2-VL
- Qwen3-Next

另外接触过 diffusion、embedding 和 reranker 工作负载，包括 Stable Diffusion / SD-Turbo、BGE-small 和 BGE reranker small。

## 架构差异与 Runtime 关注点

| 架构类型 | Runtime 关注点 |
| --- | --- |
| Dense Transformer | KV cache、continuous batching、prefill / decode |
| Hybrid attention + recurrent | KV state、recurrent state、state lifetime |
| VLM | visual encoder、multimodal preprocessing、heterogeneous execution |
| MoE | routing、expert placement、communication / memory pressure |
| Looped Transformer | repeated-layer execution、index / metadata reuse |
| Diffusion | iterative execution、activation lifetime、scheduler behavior |

模型切换不仅改变参数规模，也会改变 state、memory 和 execution pattern，因此不同架构被用于观察不同 runtime path。
