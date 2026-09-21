# vLLM Runtime 基础

本文整理学习 LLM inference runtime 时最常用的一组概念，并说明它们在 serving path 中的大致位置。

## 1. Request Lifecycle

一个典型请求可以简化为：

```text
request arrival
  → admission / scheduling
  → prefill
  → decode
  → completion
```

真实系统还会包含 KV cache 分配、batch 组织、memory management、kernel execution、stream synchronization 等步骤。

## 2. Prefill

Prefill 处理输入 prompt。

主要特点：

- 一次处理多个输入 token；
- 计算量通常高于单步 decode；
- 会生成后续 decode 所需要的 KV cache；
- 长 prompt 会显著影响 TTFT。

## 3. Decode

Decode 在已有 KV cache 的基础上逐 token 生成输出。

主要特点：

- 每一步通常只新增一个 token；
- 会不断读取历史 KV cache；
- 单步计算量较小，但需要执行很多次；
- TPOT 对 decode path 很敏感。

## 4. KV Cache

Transformer attention 在 decode 时需要使用历史 token 的 Key / Value state。

KV cache 的作用是避免每生成一个新 token 都重新计算全部历史 token。

它同时也是 inference serving 中重要的显存消费者，因此会影响：

- 可并发 request 数；
- admission；
- preemption；
- prefix cache；
- memory pressure；
- batch size。

## 5. Continuous Batching

传统 batching 往往要求一组请求同时开始、同时结束。

Continuous batching 允许：

- 新请求动态加入；
- 已完成请求动态退出；
- prefill 与 decode request 在运行时持续重新组合。

因此 scheduler 会直接影响：

- GPU utilization；
- TTFT；
- TPOT；
- throughput；
- fairness；
- tail latency。

## 6. Scheduler

Scheduler 决定当前 step 中哪些 request 可以执行，以及分配多少 token / resource budget。

分析 scheduler 时通常关注：

- waiting / running request；
- token budget；
- KV cache availability；
- prefill / decode priority；
- preemption；
- batching decision。

## 7. CUDA Graph

CUDA Graph 可以减少重复 kernel launch 的 CPU overhead，但也会引入：

- graph capture；
- shape / execution constraints；
- initialization overhead；
- cold-start 与 steady-state 差异。

因此 benchmark 时需要明确是否启用了 CUDA Graph，以及第一次运行是否包含 capture / compilation cost。

## 8. 常用指标

### TTFT

**Time To First Token**

从请求进入系统到第一个输出 token 返回的时间。

主要受到：

- queueing；
- prefill；
- scheduler；
- initialization / compilation；

等因素影响。

### TPOT

**Time Per Output Token**

首 token 之后，每生成一个新 token 的平均时间。

通常更能反映 decode path 的持续性能。

### Throughput

常见形式包括：

- requests / second；
- input tokens / second；
- output tokens / second；
- total tokens / second。

比较 throughput 时必须保证 workload 定义一致。

### Tail Latency

例如 p95 / p99 latency。

平均值可能掩盖少量非常慢的请求，因此 serving systems 通常还需要看 tail behavior。

## 9. Runtime 分析的基本思路

看到性能变化后，不应直接把变化归因给某个机制。

更可靠的链路是：

```text
workload
  → scheduler / memory / execution change
  → runtime event
  → latency / throughput change
```

因此后续学习重点通常会从 benchmark 逐步进入 profiling、trace 与源码分析。
