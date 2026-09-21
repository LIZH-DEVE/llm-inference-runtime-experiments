# 模型与架构矩阵

本文件记录已经实际用于本地实验的模型，以及源码阅读和机制分析中涉及的其他模型家族。

## 1. 本地完整 inference / runtime 实验

### Qwen3-1.7B

- 架构：dense Transformer
- 主要 dtype：BF16
- 用途：
  - vLLM engine smoke test
  - request / scheduler / KV state 实验
  - runtime instrumentation
  - quantization / state-related probe
- 当前角色：本地最常用的 dense control model

### Qwen3.5-2B

- 架构：hybrid
- 用途：
  - attention 与 recurrent state 共存时的 runtime 行为
  - hybrid cache / state lifetime 分析
  - 本地结构性 gate 与机制验证

### Qwen3-VL-2B-Instruct

- 架构：Vision-Language Model
- 用途：
  - visual encoder load
  - multimodal request path
  - encoder execution
  - CUDA Graph / eager execution 对比
  - memory / execution-path 观察

### Qwen2.5-3B-Instruct

- 架构：dense Transformer
- 用途：
  - 早期 vLLM serving 实验
  - chunked-prefill sensitivity
  - async scheduling reproduction
  - cold-start / JIT / CUDA Graph measurement calibration

## 2. 部分执行路径 / kernel 级验证

### Falcon-H1-0.5B

- 结构包含 recurrent / Mamba-like execution path
- 已实际运行 fast path 与 recurrent kernel
- 当时完整 logits correctness 尚未闭环，因此不列为“完整 inference 已验证”

### Qwen3.5-0.8B

- 用于早期 hybrid runtime / gate 实验
- 主要价值是快速验证 hybrid state path，而不是作为最终 evaluation model

### Ouro-1.4B

- looped Transformer
- 用于循环层执行、索引复用与 metadata 行为实验

## 3. 源码 / 机制研究涉及的其他模型家族

下面这些模型或架构用于源码阅读、机制对比或研究问题扫描，不等同于都在当前 RTX 5060 上完成了完整推理验证：

- Llama-3
- LLaVA
- Mixtral
- DeepSeek-MoE
- Jamba
- Mamba
- Zamba
- Qwen2-VL
- Qwen3-Next

此外也接触过 diffusion / embedding / reranker 工作负载，例如：

- Stable Diffusion / SD-Turbo / Tiny / distilled diffusion variants
- BGE-small
- BGE reranker small

## 4. 为什么要覆盖不同模型结构

对 inference runtime 来说，“模型不同”不只是参数量变化。

不同结构会改变系统需要管理的状态和执行路径：

| 架构类型 | 典型 runtime 关注点 |
| --- | --- |
| Dense Transformer | KV cache、continuous batching、prefill/decode |
| Hybrid attention + recurrent | KV state + recurrent state lifetime |
| VLM | visual encoder、multimodal preprocessing、heterogeneous execution |
| MoE | routing、expert placement、communication / memory pressure |
| Looped Transformer | repeated-layer execution、index / metadata reuse |
| Diffusion | iterative denoising loop、activation / scheduler behavior |

因此模型覆盖的目的不是“跑过多少模型”，而是建立对不同 runtime state、memory 和 execution pattern 的基本认识。
