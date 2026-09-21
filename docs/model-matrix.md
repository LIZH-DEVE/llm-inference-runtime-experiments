# 模型与架构矩阵

该文档记录本地 runtime 实验中使用过的模型，以及源码分析过程中对比过的模型家族。

## 本地 Runtime 实验

| 模型 | 架构 | 验证内容 |
| --- | --- | --- |
| **Qwen3-1.7B** | Dense Transformer | BF16 inference、request / scheduler / KV state、runtime tracing |
| **Qwen3.5-2B** | Hybrid | attention 与 recurrent state、state lifetime |
| **Qwen3-VL-2B-Instruct** | Vision-Language Model | visual encoder、multimodal request path、CUDA Graph / eager execution |
| **Qwen2.5-3B-Instruct** | Dense Transformer | serving、chunked prefill、async scheduling、measurement calibration |
| **Falcon-H1-0.5B** | Hybrid / recurrent | fast path、recurrent kernel |
| **Qwen3.5-0.8B** | Hybrid | 轻量 runtime mechanism 验证 |
| **Ouro-1.4B** | Looped Transformer | repeated-layer execution、index / metadata reuse |

## 源码与架构对比

源码阅读和机制分析还涉及：

- Llama-3
- LLaVA
- Mixtral
- DeepSeek-MoE
- Jamba
- Mamba
- Zamba
- Qwen2-VL
- Qwen3-Next

另外也接触过 diffusion、embedding 与 reranker 工作负载，包括 Stable Diffusion / SD-Turbo、BGE-small 与 BGE reranker small。

## 架构差异与 Runtime 关注点

| 架构类型 | Runtime 关注点 |
| --- | --- |
| Dense Transformer | KV cache、continuous batching、prefill / decode |
| Hybrid attention + recurrent | KV state、recurrent state、state lifetime |
| VLM | visual encoder、multimodal preprocessing、heterogeneous execution |
| MoE | routing、expert placement、communication / memory pressure |
| Looped Transformer | repeated-layer execution、index / metadata reuse |
| Diffusion | iterative execution、activation lifetime、scheduler behavior |

不同模型结构对应不同的 state、memory 和 execution pattern，因此模型切换同时也是 runtime mechanism 的切换。
