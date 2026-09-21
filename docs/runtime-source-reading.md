# vLLM Runtime Source Map

当前源码阅读以 **vLLM 0.26.0 V1 runtime** 为主。重点不是整理概念，而是跟踪 request state、scheduler decision、KV allocation 与 model execution 之间的实际代码路径。

## Scheduler

### `vllm/v1/core/sched/scheduler.py`

核心类：

```text
Scheduler
```

重点入口：

```text
Scheduler.schedule()
```

该函数维护并使用：

- `self.running`
- `self.waiting`
- `self.max_num_scheduled_tokens`
- `token_budget`
- `num_scheduled_tokens`
- `preempted_reqs`

典型路径：

```text
RUNNING requests
  → compute num_new_tokens
  → KVCacheManager.allocate_slots()
  → possible preemption
  → update num_scheduled_tokens
  → consume token_budget

WAITING requests
  → cache lookup / resource checks
  → allocate slots
  → move into running
```

vLLM V1 scheduler 不把执行简单划分成独立的“prefill scheduler”和“decode scheduler”。调度基于 request 当前的 `num_computed_tokens` 与待计算 token 数统一进行。

## Scheduler Output

### `vllm/v1/core/sched/output.py`

`SchedulerOutput` 是 scheduler 与后续 model execution 之间的重要边界。

当前 tracing 主要使用：

- `num_scheduled_tokens: dict[str, int]`
- `total_num_scheduled_tokens`
- `scheduled_new_reqs`
- `scheduled_cached_reqs`
- `preempted_req_ids`
- `finished_req_ids`

这些字段可以把 request-level latency 与具体 scheduler step 对齐。

## Request State

### `vllm/v1/request.py`

分析 request lifecycle 时重点关注：

- request id；
- prompt / output token state；
- `num_computed_tokens`；
- output placeholders；
- request status；
- preemption count；
- encoder / multimodal inputs。

对于 runtime 分析，重要的是区分：

```text
logical request state
vs.
tokens actually scheduled in this step
vs.
GPU-side cache / execution state
```

## KV Cache

### `vllm/v1/core/kv_cache_manager.py`

scheduler 通过 KV cache manager 完成 block 查找和 slot allocation。

重点路径包括：

- prefix-cache lookup；
- `allocate_slots()`；
- block free / reuse；
- preemption 后的 state handling。

在 hybrid model 中，还需要继续跟踪 Mamba / recurrent state 与 attention KV state 的不同生命周期。

## Scheduler Configuration

### `vllm/config/scheduler.py`

实验中经常涉及的配置包括：

- `max_num_seqs`
- `max_num_batched_tokens`
- scheduling policy
- async scheduling
- chunked prefill 相关参数

这些参数影响 scheduler 可达的 batch state，因此 benchmark 必须与 runtime flags 一起记录。

## Multimodal Path

VLM request 还需要继续追踪：

```text
input preprocessing
  → multimodal feature / encoder budget
  → encoder cache
  → language-model scheduling
```

相关路径分布在 `vllm/multimodal/`、encoder cache manager 和 scheduler 中。

## 从源码观察到实验

源码中的特殊 branch、fallback 或 TODO 只作为实验入口。

后续分析按以下顺序推进：

```text
source path
  → trigger condition
  → runtime event
  → controlled workload
  → request-level measurement
```

公开的 scheduler tracing adapter 位于：

- [`instrumentation/vllm_scheduler_trace.py`](../instrumentation/vllm_scheduler_trace.py)
- [`instrumentation/request_correlated_trace.py`](../instrumentation/request_correlated_trace.py)
