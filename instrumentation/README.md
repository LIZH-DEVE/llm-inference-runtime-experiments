# Request-Correlated Runtime Tracing

该目录保存一个轻量级 request-correlated trace 示例，用于把 scheduler 状态与请求级执行过程关联起来。

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

## Trace Example

```text
scheduler_step
  ├── iteration_id
  ├── running_count
  ├── waiting_count
  └── token_budget_remaining

request_scheduled
  ├── request_id
  ├── iteration_id
  ├── scheduled_tokens
  └── preempted
```

## Implementation Notes

实现采用：

- `time.perf_counter_ns()` 作为单调时钟；
- append-only JSONL；
- buffered flush；
- 固定、紧凑的字段集合；
- hot path 中不执行复杂分析。

实际分析在 trace 写出后离线完成，减少 tracing 对 scheduler path 的额外干扰。

示例代码见 [request_correlated_trace.py](request_correlated_trace.py)。
