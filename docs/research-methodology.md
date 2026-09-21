# Research Methodology

本仓库中的实验遵循一个简单原则：先确认现象，再解释机制。

## 基本流程

```text
Observation
  → Reproduction
  → Confounder Control
  → Instrumentation
  → Attribution
  → Keep / Revise / Kill
```

## 1. Observation

初始观察只说明“某个配置下出现差异”。

它不能直接证明：

- scheduler 是原因；
- CUDA Graph 是原因；
- KV cache 是原因；
- 某个优化一定有效。

## 2. Reproduction

重复运行并固定：

- model；
- dtype；
- workload；
- context length；
- output length；
- runtime flags；
- warmup；
- random seed（需要时）。

如果信号不能稳定复现，先停止机制解释。

## 3. Confounder Control

优先排查：

- cold-start；
- JIT compilation；
- CUDA Graph capture；
- prefix-cache hit；
- execution mode；
- server startup / shutdown；
- logging / flush；
- request ordering；
- measurement noise。

## 4. Instrumentation

只有 latency 数字通常无法说明机制。

Instrumentation 应尽量记录最小必要信息，例如：

- request id；
- scheduler iteration；
- scheduled tokens；
- running / waiting count；
- preemption；
- execution phase。

同时需要检查 instrumentation 是否本身改变结果。

## 5. Attribution

理想证据链：

```text
runtime state change
  → specific event / path change
  → measurable performance effect
```

如果只能看到性能相关性，应保留“correlation”表述，不直接升级为 mechanism claim。

## 6. Kill

当以下情况出现时应停止原假设：

- 更严格实验无法复现；
- 简单 confounder 已足以解释现象；
- instrumentation 改变信号方向；
- magnitude 收缩到噪声级别；
- 新结果与原机制预测冲突。

Negative result 不是失败记录，而是下一轮选题和实验设计的约束。
