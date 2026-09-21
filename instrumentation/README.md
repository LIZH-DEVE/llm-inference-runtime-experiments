# Request-Correlated Runtime Tracing

该目录提供一个面向 **vLLM V1 scheduler** 的轻量 request-level trace。

当前 adapter 针对 vLLM 0.26.x 的 `Scheduler.schedule()` API，记录 scheduler step 与 request-level scheduling decision，不序列化完整 `Request` 对象。

## 记录内容

### Scheduler Step

```text
scheduler_step
  ├── iteration_id
  ├── running_count
  ├── waiting_count
  └── token_budget_remaining
```

### Request Scheduling

```text
request_scheduled
  ├── request_id
  ├── iteration_id
  ├── scheduled_tokens
  ├── running_count
  ├── waiting_count
  ├── token_budget_remaining
  └── preempted
```

如果某个 request 在该 step 被 preempt，还会记录 `request_preempted`。

## Event Schema

| Field | Meaning |
| --- | --- |
| `timestamp_ns` | monotonic timestamp |
| `event` | event type |
| `request_id` | request identity |
| `iteration_id` | scheduler iteration |
| `scheduled_tokens` | tokens assigned in the current step |
| `running_count` | number of running requests |
| `waiting_count` | number of waiting requests |
| `token_budget_remaining` | remaining scheduler token budget |
| `preempted` | whether the request was preempted |

## 使用方式

必须在创建 vLLM engine **之前**安装 wrapper：

```python
from instrumentation.request_correlated_trace import JsonlRuntimeTrace
from instrumentation.vllm_scheduler_trace import install_scheduler_trace

trace = JsonlRuntimeTrace("results/scheduler-trace.jsonl")
install_scheduler_trace(trace)

from vllm import LLM
# construct LLM after installing the wrapper
```

完整最小示例：

```bash
python examples/traced_vllm_smoke_test.py \
  --model Qwen/Qwen3-1.7B
```

## 实现原则

- 使用 `time.perf_counter_ns()` 单调时钟；
- JSONL append-only 输出；
- buffered flush；
- hot path 中不做离线统计；
- 不写入 prompt / token content；
- 每个 scheduler step 只记录必要的 queue / token metadata。

trace 分析与 runtime 执行分离，避免在 scheduler path 中加入复杂聚合逻辑。
