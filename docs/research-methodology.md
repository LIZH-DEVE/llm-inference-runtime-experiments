# Experiment Methodology

Runtime 性能实验首先确认现象是否稳定，再进入机制分析。

## 实验流程

```text
Observation
  → Reproduction
  → Confounder Control
  → Instrumentation
  → Attribution
  → Retain / Revise / Discard
```

## 1. Observation

初始结果只用于确认某个配置下是否存在可测差异，不直接用于判断原因。

## 2. Reproduction

重复实验时固定：

- model；
- dtype；
- workload；
- context length；
- output length；
- runtime flags；
- warmup；
- random seed（需要时）。

只有稳定复现的现象才继续进入机制分析。

## 3. Confounder Control

优先检查：

- cold start；
- JIT compilation；
- CUDA Graph capture；
- prefix-cache hit；
- execution mode；
- server startup / shutdown；
- logging / flush；
- request ordering；
- measurement noise。

## 4. Instrumentation

当 latency / throughput 结果不足以解释原因时，再加入 runtime tracing。

常用字段包括：

- request id；
- scheduler iteration；
- scheduled tokens；
- running / waiting count；
- preemption；
- execution phase。

同时对 tracing 本身的额外开销进行检查。

## 5. Attribution

目标是建立：

```text
runtime state change
  → execution-path change
  → measurable performance effect
```

如果 trace 只能支持相关性，则结论保持在 correlation 层面。

## 6. Result Revision

出现以下情况时，原始解释需要修正或停止：

- 更严格实验无法复现；
- cold start、JIT 或 execution mode 已能解释主要差异；
- instrumentation 明显改变目标信号；
- 性能差异收缩到 run-to-run variance 附近；
- 新结果与原先机制预测不一致。

这些结果会继续保留在 case studies 中，用于记录实验条件和后续修正。
