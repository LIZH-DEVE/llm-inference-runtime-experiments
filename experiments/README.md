# Controlled Streaming Benchmark

该目录保存一个面向 vLLM OpenAI-compatible server 的 request-level benchmark。

## Server

先启动 vLLM server，例如：

```bash
vllm serve Qwen/Qwen3-1.7B \
  --dtype bfloat16 \
  --max-model-len 2048
```

也可以使用当前环境中的其他模型。

## Benchmark

```bash
python experiments/streaming_benchmark.py \
  --model Qwen/Qwen3-1.7B \
  --warmup 2 \
  --requests 16 \
  --concurrency 4 \
  --max-tokens 64 \
  --output results/benchmark.jsonl
```

输出 JSONL 包含三类 record：

```text
metadata
request
run_summary
```

每个成功 request 记录：

- TTFT
- TPOT
- end-to-end latency
- output token count

run summary 记录：

- wall-clock duration
- successful / failed requests
- requests / second
- output tokens / second

## Analysis

```bash
python scripts/analyze_benchmark.py results/benchmark.jsonl
```

输出 request-level mean / median / p95 / p99，以及 run-level throughput。

## Measurement Controls

脚本显式区分：

```text
warmup requests
vs.
measured requests
```

并固定：

- model
- output token budget
- client concurrency
- generation temperature
- prompt construction

该 harness 主要用于 runtime sensitivity 和 reproduction，不代替 production-scale serving benchmark。
