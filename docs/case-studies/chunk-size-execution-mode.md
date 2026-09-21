# Chunk-size × Execution Mode

## Environment

```text
GPU: RTX 5060 Laptop 8 GB
Model: Qwen2.5-3B
Runtime: historical vLLM 0.21.0-era experiment
```

## Initial Observation

不同 chunk-size 配置最初表现出约 **30.9%** 的性能差异。

## Control

复测时固定：

- model / workload；
- warmup；
- request configuration；
- execution mode。

并使用 eager 路径单独排除 CUDA Graph compilation / specialization 的影响。

## Result

原来的约 30.9% 差异缩小到约 **2.3%**。

## Takeaway

scheduler 参数与 GPU execution mode 不能混在同一个未控制的对比中。

对 chunking、batching 或 scheduler 参数做 sensitivity test 时，需要同时记录 graph / eager execution path。
