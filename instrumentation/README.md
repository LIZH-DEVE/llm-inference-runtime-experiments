# Runtime Instrumentation

本目录给出一个简化的 request-correlated event trace 示例。

目标不是提供完整 profiler，而是展示 runtime instrumentation 的基本设计：

```text
request_id
+ scheduler iteration
+ event type
+ token / queue metadata
+ timestamp
```

## Event Schema

示例字段：

| Field | Meaning |
| --- | --- |
| timestamp_ns | monotonic timestamp |
| event | event type |
| request_id | request identity |
| iteration_id | scheduler step |
| scheduled_tokens | tokens assigned in this step |
| running_count | running requests |
| waiting_count | waiting requests |
| token_budget_remaining | scheduler budget |
| preempted | whether request was preempted |

## Design Principles

- request-correlated；
- append-only JSONL；
- monotonic clock；
- 低字段数量；
- 支持 batch flush；
- 不在 hot path 做复杂分析。

实际研究 instrumentation 还会根据问题增加特定 event，但应先证明新增 trace 不会显著扰动目标 signal。
