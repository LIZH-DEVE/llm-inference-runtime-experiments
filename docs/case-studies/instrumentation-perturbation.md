# Instrumentation Perturbation

## Problem

为了理解 scheduler behavior，早期实验加入了 request-correlated tracing。

第一版 trace 在每个 scheduler step 写入较完整的 running-request snapshot。

## Observation

重 tracing 产生了大量 trace 数据，并明显改变了原来的 latency signal。

在一个历史实验中，原本较明显的差异在 heavy trace 下收缩到约 **2.45%**，因此这组结果被标记为 perturbative / inconclusive。

## Revision

随后将 instrumentation 缩减为：

- scheduler iteration id；
- running / waiting count；
- short / long request count；
- scheduled request id；
- scheduled token count；
- token budget；
- preempted request id。

避免每一步序列化完整 request state。

## Lesson

Instrumentation 不是旁观者。

```text
more trace
!=
better evidence
```

如果 tracing 改变了被测 runtime，trace 本身就成为 confounder。

因此 instrumentation 设计需要同时考虑：

- information value；
- serialization cost；
- write frequency；
- synchronization；
- output volume。
