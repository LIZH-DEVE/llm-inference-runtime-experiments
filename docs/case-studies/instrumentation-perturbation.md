# Instrumentation Perturbation

## Setup

为了观察 scheduler behavior，早期版本在每个 scheduler step 写入较完整的 running-request snapshot。

## Observation

heavy trace 产生较大的 serialization / output volume，并明显改变了目标 latency signal。

在对应实验中，原本较明显的差异在 heavy trace 下收缩到约 **2.45%**，因此该 run 不再用于机制归因。

## Revision

后续 tracing 缩减为：

- scheduler iteration；
- request id；
- scheduled tokens；
- running / waiting count；
- token budget；
- preemption。

完整 request state 不再在 hot path 中序列化。

## Takeaway

Instrumentation 本身也属于实验系统的一部分。

设计 tracing 时同时考虑：

- information value；
- serialization cost；
- write frequency；
- synchronization；
- output volume。

当前仓库中的 [request-correlated tracing](../../instrumentation/README.md) 延续了这一轻量化思路。
