# LLM Inference Runtime Foundations

面向 **LLM inference / serving systems** 的基础实践仓库，记录本地 GPU 环境配置、vLLM 运行验证、推理 runtime 基础概念、benchmark 方法和常见排障过程。

内容围绕可复现的本地推理环境、vLLM 基础运行链路、常用 serving 指标与 benchmark 方法展开。

## 当前环境

当前已验证的本地环境：

| 组件 | 配置 |
| --- | --- |
| GPU | NVIDIA RTX 5060 Laptop，8 GB |
| GPU 架构 | Blackwell，sm_120 |
| 系统 | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |
| 本地模型 | Qwen3-1.7B，BF16 |

这套环境主要用于源码阅读、小规模 inference profiling、runtime 行为复现和实验方法训练。

## 仓库内容

```text
.
├── README.md
├── docs/
│   ├── environment-setup.md
│   ├── vllm-runtime-basics.md
│   ├── benchmark-methodology.md
│   └── troubleshooting/
│       └── wsl-cuda-vllm-checklist.md
├── examples/
│   └── vllm-smoke-test.py
└── scripts/
    ├── collect_environment.py
    └── summarize_latency.py
```

## Quick Start

### 1. 检查环境

```bash
python scripts/collect_environment.py
```

脚本会输出 Python、PyTorch、CUDA、GPU 与 vLLM 的基础版本信息。

### 2. 运行最小 vLLM smoke test

```bash
python examples/vllm-smoke-test.py \
  --model Qwen/Qwen3-1.7B
```

该脚本只验证最小离线推理链路：

```text
model load
  -> request
  -> prefill
  -> decode
  -> output
```

### 3. 汇总 latency JSONL

```bash
python scripts/summarize_latency.py run.jsonl --field ttft_ms
```

输出 count、mean、median、p95、p99、min 和 max。

## 学习重点

### Runtime

重点理解：

- request lifecycle；
- scheduler；
- prefill / decode；
- KV cache；
- continuous batching；
- CUDA Graph；
- execution mode；
- CPU / GPU synchronization。

### Serving Metrics

常用指标：

- **TTFT**：Time To First Token，请求到首 token 返回的时间；
- **TPOT**：Time Per Output Token，首 token 之后平均生成一个 token 的时间；
- **Latency**：单请求端到端延迟；
- **Throughput**：单位时间内完成的请求或生成的 token 数；
- **Tail Latency**：例如 p95 / p99 latency，用于观察慢请求。

### Benchmark

基础测量原则：

- 区分 cold start 与 steady state；
- 正式测量前进行 warmup；
- 使用重复实验而不是单次结果；
- 固定模型、dtype、context length 与 runtime flags；
- 同时记录环境、workload 和版本信息；
- 在解释小幅性能差异前先检查方差与 measurement noise。

详细内容见 [Benchmark Methodology](docs/benchmark-methodology.md)。

## 文档入口

- [环境搭建与验证](docs/environment-setup.md)
- [vLLM Runtime 基础](docs/vllm-runtime-basics.md)
- [Benchmark 方法](docs/benchmark-methodology.md)
- [WSL / CUDA / vLLM 排障清单](docs/troubleshooting/wsl-cuda-vllm-checklist.md)

## 定位

本仓库记录 **LLM inference runtime 基础工程实践**，重点是环境、运行链路、测量方法和基础工具。
