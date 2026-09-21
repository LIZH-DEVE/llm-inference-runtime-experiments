# LLM Inference Runtime：实验与分析

围绕 **vLLM 与单机 GPU 推理运行时**，整理本地运行环境、不同模型架构、runtime 源码分析、request-level tracing，以及若干已经完成的受控实验。

当前内容主要覆盖：

- vLLM request lifecycle、scheduler、prefill / decode 与 KV cache；
- dense、hybrid、VLM、looped Transformer 等不同执行形态；
- CUDA Graph、JIT、execution mode 对性能测量的影响；
- request-correlated runtime tracing；
- warmup、重复测量与 instrumentation overhead 控制。

## 实验平台

| 组件 | 配置 |
| --- | --- |
| GPU | NVIDIA RTX 5060 Laptop，8 GB |
| GPU 架构 | Blackwell，sm_120 |
| 系统 | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |

这套环境用于模型运行验证、runtime tracing、小规模 profiling 和机制复现。

## 模型与架构

### 已用于本地 runtime 实验

| 模型 | 架构 | 主要实验内容 |
| --- | --- | --- |
| **Qwen3-1.7B** | Dense Transformer | BF16 inference、scheduler / KV state、runtime tracing |
| **Qwen3.5-2B** | Hybrid | attention / recurrent state、state lifetime |
| **Qwen3-VL-2B-Instruct** | VLM | visual encoder、multimodal execution、CUDA Graph |
| **Qwen2.5-3B-Instruct** | Dense Transformer | serving、chunked prefill、async scheduling、测量校准 |
| **Falcon-H1-0.5B** | Hybrid / recurrent | fast path 与 recurrent kernel 验证 |
| **Qwen3.5-0.8B** | Hybrid | 轻量 runtime mechanism 验证 |
| **Ouro-1.4B** | Looped Transformer | repeated-layer execution、index / metadata reuse |

源码阅读和架构对比还涉及 Llama-3、LLaVA、Mixtral、DeepSeek-MoE、Jamba、Mamba、Zamba、Qwen2-VL、Qwen3-Next 等模型家族。

详见 [模型与架构矩阵](docs/model-matrix.md)。

## Runtime 分析范围

当前主要跟踪以下路径：

```text
request arrival
  → admission / scheduler
  → prefill / decode
  → KV / recurrent state
  → model execution
  → output / completion
```

重点包括：

- request waiting / running lifecycle；
- continuous batching；
- prefill / decode interaction；
- KV cache allocation、reuse 与 reclaim；
- hybrid model recurrent state；
- CUDA Graph / eager execution；
- multimodal encoder path；
- tracing 对 runtime 本身的影响。

详见 [Runtime 源码分析](docs/runtime-source-reading.md)。

## Runtime Tracing

在本地 vLLM scheduler 路径中使用 request-correlated tracing，将调度状态与请求级结果关联起来。

记录字段包括：

- request id；
- scheduler iteration；
- scheduled tokens；
- running / waiting request count；
- token budget；
- preemption；
- monotonic timestamp。

仓库中保留了一个精简版本：

- [Tracing 设计说明](instrumentation/README.md)
- [Request-correlated trace 示例](instrumentation/request_correlated_trace.py)

## 代表性实验

| 实验 | 初始现象 | 控制后结果 | 主要结论 |
| --- | --- | --- | --- |
| **CUDA Graph / cold start** | 表面差异约 **233.7%** | steady-state 下约 **9.9%** | initialization / compilation 会显著放大首轮结果 |
| **Chunk-size sensitivity** | 配置间差异约 **30.9%** | 控制 execution mode 后约 **2.3%** | chunk 参数实验必须同时固定 execution path |
| **Async scheduling** | 初始出现 HOL blocking 信号 | 加强重复测量后未稳定复现 | 原始 scheduler 解释不成立 |
| **Tracing overhead** | heavy trace 下原信号明显收缩 | 改为轻量 request-correlated trace | instrumentation 本身可能成为性能干扰项 |

详细记录见 [Case Studies](docs/case-studies/README.md)。

## 实验方法

运行时性能实验统一关注四类信息：

```text
workload
  → runtime state
  → execution event
  → observed metric
```

测量时优先控制：

- warmup / cold start；
- JIT / CUDA Graph capture；
- model、dtype 与 workload；
- request ordering；
- execution mode；
- tracing overhead；
- run-to-run variance。

详见 [实验方法](docs/research-methodology.md)。

## 仓库结构

```text
.
├── README.md
├── docs/
│   ├── environment-setup.md
│   ├── model-matrix.md
│   ├── runtime-source-reading.md
│   ├── research-methodology.md
│   ├── case-studies/
│   └── troubleshooting/
├── instrumentation/
│   ├── README.md
│   └── request_correlated_trace.py
├── examples/
│   └── vllm-smoke-test.py
└── scripts/
    └── collect_environment.py
```
