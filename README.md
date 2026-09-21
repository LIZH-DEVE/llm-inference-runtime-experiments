# LLM Inference Runtime Research Practice

面向 **LLM inference / serving systems** 的公开科研实践仓库。

这里不只记录环境搭建，而是集中展示我在本科阶段进行 AI Infra / LLM inference 学习和实验时形成的几类基础能力：

- 搭建并维护可运行的 GPU inference stack；
- 在 dense、hybrid、VLM、looped 等不同模型结构上验证 runtime 行为；
- 阅读 vLLM 源码并梳理 request / scheduler / KV cache / execution path；
- 设计 request-correlated runtime instrumentation；
- 进行 controlled experiment，区分 cold-start、CUDA Graph、JIT、execution mode 等混杂因素；
- 对无法稳定复现的现象主动证伪，而不是只保留正结果。

## 1. 当前实验平台

| 组件 | 当前配置 |
| --- | --- |
| GPU | NVIDIA RTX 5060 Laptop，8 GB |
| GPU 架构 | Blackwell，sm_120 |
| 系统 | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |

环境搭建只是仓库的一部分。更重要的是利用这套本地平台进行 runtime source analysis、profiling、instrumentation 和 cheap falsification。

## 2. 模型覆盖

实际实验并不只使用 Qwen 系列。

### 本地完整 inference / runtime 实验

| 模型 | 架构 / 用途 |
| --- | --- |
| **Qwen3-1.7B** | dense Transformer；当前主要 BF16 runtime 实验模型 |
| **Qwen3.5-2B** | hybrid model；用于 recurrent / attention state 与 runtime 行为实验 |
| **Qwen3-VL-2B-Instruct** | VLM；用于 visual encoder、multimodal execution 与 CUDA Graph 相关实验 |
| **Qwen2.5-3B-Instruct** | 早期 vLLM serving、chunked-prefill 与 measurement 实验 |

### 部分执行路径 / 机制验证

| 模型 | 状态 |
| --- | --- |
| **Falcon-H1-0.5B** | 已运行 fast path / Mamba recurrent kernel；完整 logits correctness 当时未闭环 |
| **Qwen3.5-0.8B** | 用于早期 hybrid runtime / gate 验证 |
| **Ouro-1.4B** | looped Transformer；用于循环层与索引复用相关实验 |

另外还阅读或对比过 **Llama-3、LLaVA、Mixtral、DeepSeek-MoE、Jamba、Mamba / Zamba、Qwen2-VL、Qwen3-Next** 等模型或架构。这里区分“完整本地推理通过”和“源码 / 机制研究涉及”，避免把两者混为一谈。

详见 [模型与架构矩阵](docs/model-matrix.md)。

## 3. Runtime Source Analysis

当前重点阅读和实验的 runtime 问题包括：

```text
request arrival
  → admission / scheduler
  → prefill / decode
  → KV / persistent state
  → model execution
  → output / completion
```

重点关注：

- request lifecycle；
- waiting / running state；
- continuous batching；
- prefill / decode interaction；
- KV cache allocation / reuse；
- hybrid recurrent state；
- CUDA Graph / eager execution；
- multimodal encoder execution；
- instrumentation 对系统本身的扰动。

详见 [Runtime 源码阅读记录](docs/runtime-source-reading.md)。

## 4. Runtime Instrumentation

我曾在本地 vLLM scheduler 路径中做 request-correlated tracing，用于关联：

- request id；
- scheduled tokens；
- running / waiting request 数量；
- prefill / decode state；
- token budget；
- preemption；
- scheduler iteration。

公开仓库保留一个经过简化的 instrumentation 示例，用于展示 event schema 和低侵入 trace 设计：

- [Instrumentation 说明](instrumentation/README.md)
- [Minimal request-correlated trace](instrumentation/request_correlated_trace.py)

完整研究版 instrumentation 和 active experiments 保存在私有研究工作区。

## 5. Controlled Experiments

公开保留三组已经结束、适合展示实验方法的案例。

### Case A — Cold-start / CUDA Graph artifact

一次早期实验中观察到约 **233.7%** 的表面性能差异。

加入 warmup、区分 initialization 与 steady-state 后，差异收缩到约 **9.9%**。

说明：如果不控制 JIT / CUDA Graph capture / initialization，可能把一次性成本误认为稳定 runtime behavior。

### Case B — Chunk-size sensitivity

早期不同 chunk-size 配置表现出约 **30.9%** 的差异。

控制 execution mode、使用 eager 路径重新测量后，差异缩小到约 **2.3%**。

说明：scheduler / chunking 参数实验必须控制 execution mode。

### Case C — Async scheduling reproduction

早期观察到 async scheduling 相关的 head-of-line blocking 信号。

增加 warmup、重复测量、graceful shutdown 和完整 log flush 后，该信号没有稳定复现；原假设因此停止。

这三组案例的价值不在“优化了多少”，而在于展示：

```text
observation
  → confounder inspection
  → controlled reproduction
  → attribution
  → keep / revise / kill
```

详见 [实验案例](docs/case-studies/README.md)。

## 6. 仓库结构

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

## 7. 当前定位

这个仓库用于公开展示 **LLM inference systems 的基础科研实践**：

> 环境与模型运行 → 源码阅读 → instrumentation → controlled experiment → falsification

更具体的研究候选、raw data、paper drafts 和当前正在推进的实验不放在公开仓库中。
