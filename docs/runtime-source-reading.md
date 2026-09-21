# Runtime 源码阅读记录

本文件记录 LLM inference runtime 源码阅读时关注的主要对象和问题。

## 1. Request Lifecycle

阅读 request path 时重点追踪：

```text
request created
  → admitted / queued
  → scheduled
  → model execution
  → output produced
  → request finished / cancelled / preempted
```

需要区分 logical request state 与 GPU 上实际资源状态。

## 2. Scheduler

重点关注：

- waiting request；
- running request；
- token budget；
- prefill / decode request 的共同调度；
- preemption；
- max-num-seqs / max-num-batched-tokens 等资源约束；
- scheduler decision 如何映射到真正的 GPU execution。

仅观察最终 latency 不足以解释 scheduler mechanism，因此需要 request-correlated trace。

## 3. KV Cache / Persistent State

Dense Transformer 中主要关注：

- block allocation；
- block table；
- reuse；
- prefix caching；
- request completion 后的 free / reclaim；
- preemption / recompute。

对于 hybrid model，还需要继续考虑：

- recurrent state；
- conv state；
- 不同 state 的 lifetime / ownership；
- attention KV 与 recurrent state 是否共享相同调度假设。

## 4. Prefill / Decode

Prefill 和 decode 的资源特性不同：

- prefill 通常一次处理更多 token；
- decode 每 step 新增少量 token，但持续时间长；
- 两者混合时可能产生 latency / throughput trade-off。

因此实验中需要明确 workload composition，而不是只给一个 batch size。

## 5. CUDA Graph / Eager Execution

CUDA Graph 可以降低重复 launch overhead，但同时会引入：

- graph capture；
- graph specialization；
- shape constraints；
- cold-start cost；
- eager fallback。

性能实验必须记录 execution mode，否则 scheduler 参数变化可能和 CUDA Graph 行为混在一起。

## 6. Multimodal Runtime

VLM 不只是“LLM 多一个图像输入”。

需要继续追踪：

```text
image / video input
  → preprocessing
  → visual encoder
  → embedding / token preparation
  → language-model execution
```

不同阶段可能有不同：

- memory demand；
- graphability；
- execution backend；
- CPU / GPU synchronization；
- batching behavior。

## 7. Source Observation → Experiment

源码中的 TODO、特殊 branch 或 fallback 只代表实验线索。

后续至少继续问：

1. 能否稳定触发？
2. magnitude 是否足够大？
3. 是否能排除简单 explanation？
4. mechanism 是否有 trace 支持？
5. 现有实现是否已经有简单 workaround？

这一步用于把源码阅读从“找到奇怪代码”转化为可验证的 systems question。
