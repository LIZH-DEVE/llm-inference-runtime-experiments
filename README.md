# LLM Inference Runtime：源码分析、Tracing 与性能实验

围绕 **vLLM 与单机 GPU 推理运行时**，记录本地环境、模型执行路径、scheduler / KV cache 源码分析、request-level tracing，以及若干受控性能实验。

仓库当前重点是把性能数字和具体 runtime state 对齐，而不是只做模型调用或参数测试。

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

这套环境用于本地 inference、runtime tracing、小规模 profiling 与机制复现。

## 模型与架构

### 完整本地 inference / runtime 实验

| 模型 | 架构 | 主要用途 |
| --- | --- | --- |
| **Qwen3-1.7B** | Dense Transformer | BF16 inference、scheduler / KV state、runtime tracing |
| **Qwen3.5-2B** | Hybrid | attention / recurrent state、state lifetime |
| **Qwen3-VL-2B-Instruct** | VLM | visual encoder、multimodal execution、CUDA Graph |
| **Qwen2.5-3B-Instruct** | Dense Transformer | serving、chunked prefill、async scheduling、measurement calibration |

### 执行路径 / kernel 级验证

| 模型 | 架构 | 验证内容 |
| --- | --- | --- |
| **Falcon-H1-0.5B** | Hybrid / recurrent | fast path、recurrent kernel |
| **Qwen3.5-0.8B** | Hybrid | lightweight runtime path |
| **Ouro-1.4B** | Looped Transformer | repeated-layer execution、index / metadata reuse |

源码阅读和架构对比还涉及 Llama-3、LLaVA、Mixtral、DeepSeek-MoE、Jamba、Mamba、Zamba、Qwen2-VL、Qwen3-Next 等模型家族。

详见 [模型与架构矩阵](docs/model-matrix.md)。

## vLLM Runtime Source Map

当前源码阅读以 vLLM 0.26.0 V1 runtime 为主。

重点路径：

```text
vllm/v1/core/sched/scheduler.py
  → Scheduler.schedule()

vllm/v1/core/sched/output.py
  → SchedulerOutput

vllm/v1/core/kv_cache_manager.py
  → KV allocation / reuse

vllm/v1/request.py
  → Request state
```

分析对象包括：

- waiting / running request lifecycle；
- token budget；
- continuous batching；
- prefill / decode interaction；
- KV allocation / reuse / reclaim；
- preemption；
- hybrid recurrent state；
- CUDA Graph / eager execution；
- multimodal encoder path。

详见 [vLLM Runtime Source Map](docs/runtime-source-reading.md)。

## Request-Correlated Tracing

仓库包含一个针对 **vLLM V1 scheduler** 的轻量 tracing adapter。

记录：

- request id；
- scheduler iteration；
- scheduled tokens；
- running / waiting request count；
- token budget；
- preemption；
- monotonic timestamp。

核心文件：

```text
instrumentation/
├── request_correlated_trace.py
└── vllm_scheduler_trace.py
```

最小运行示例：

```bash
python examples/traced_vllm_smoke_test.py \
  --model Qwen/Qwen3-1.7B
```

离线汇总：

```bash
python scripts/analyze_trace.py results/scheduler-trace.jsonl
```

详见 [Tracing 设计说明](instrumentation/README.md)。

## Controlled Benchmark

`experiments/streaming_benchmark.py` 对运行中的 vLLM OpenAI-compatible server 发起 streaming requests，并记录：

- TTFT；
- TPOT；
- end-to-end latency；
- request throughput；
- output-token throughput；
- success / failure count。

安装客户端依赖：

```bash
pip install -r requirements.txt
```

示例：

```bash
python experiments/streaming_benchmark.py \
  --model Qwen/Qwen3-1.7B \
  --warmup 2 \
  --requests 16 \
  --concurrency 4 \
  --max-tokens 64
```

汇总结果：

```bash
python scripts/analyze_benchmark.py results/benchmark.jsonl
```

Benchmark 显式区分 warmup 与 measured requests，并固定 generation parameters 和 client concurrency。

## Measurement Case Studies

早期 runtime 实验中记录过几类典型测量问题：

| Case | 初始现象 | 控制后结果 |
| --- | --- | --- |
| **CUDA Graph / cold start** | 表面差异约 233.7% | steady-state 约 9.9% |
| **Chunk-size × execution mode** | 配置间差异约 30.9% | eager control 后约 2.3% |
| **Async scheduling** | 出现 HOL blocking 信号 | 加强复现后未稳定成立 |
| **Tracing overhead** | heavy trace 改变目标信号 | 改用轻量 request-level trace |

历史案例主要来自 RTX 5060 + Qwen2.5-3B 的早期本地 vLLM 测量阶段；当前主环境已升级到 vLLM 0.26.0。

详见 [Runtime Measurement Case Studies](docs/case-studies/README.md)。

## 实验方法

性能实验按以下链路组织：

```text
workload
  → runtime state
  → execution event
  → observed metric
```

测量时优先控制：

- warmup / cold start；
- JIT / CUDA Graph capture；
- model / dtype / workload；
- request ordering；
- execution mode；
- tracing overhead；
- run-to-run variance。

详见 [Experiment Methodology](docs/research-methodology.md)。

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
│   ├── request_correlated_trace.py
│   └── vllm_scheduler_trace.py
├── experiments/
│   └── streaming_benchmark.py
├── examples/
│   ├── vllm-smoke-test.py
│   └── traced_vllm_smoke_test.py
└── scripts/
    ├── collect_environment.py
    ├── analyze_trace.py
    └── analyze_benchmark.py
```
