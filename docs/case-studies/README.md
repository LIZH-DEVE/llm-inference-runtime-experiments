# Runtime Measurement Case Studies

这些案例来自较早的本地 vLLM 测量阶段，主要记录 performance measurement 中出现过的 confounder 和复现问题。

历史案例的主要实验环境为：

```text
GPU: RTX 5060 Laptop 8 GB
Model: Qwen2.5-3B
Runtime: vLLM 0.21.0-era local stack
```

当前仓库的主环境已经升级到 vLLM 0.26.0，因此这些数字作为历史测量案例保留，不作为当前版本的 performance baseline。

- [Cold-start / CUDA Graph](cuda-graph-cold-start.md)
- [Chunk-size × Execution Mode](chunk-size-execution-mode.md)
- [Async Scheduling Reproduction](async-scheduling-reproduction.md)
- [Instrumentation Perturbation](instrumentation-perturbation.md)
