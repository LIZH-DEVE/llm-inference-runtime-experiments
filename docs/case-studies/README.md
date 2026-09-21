# Runtime Measurement Case Studies

这些案例来自较早的本地 vLLM 测量阶段，主要记录 performance measurement 中出现过的 confounder、复现问题和后续修正。

历史案例的主要实验环境为：

```text
GPU: RTX 5060 Laptop 8 GB
Model: Qwen2.5-3B
Runtime: vLLM 0.21.0-era local stack
```

当前仓库的主环境已经升级到 vLLM 0.26.0，因此这些数字作为历史测量案例保留，不作为当前版本的 performance baseline。

公开仓库只保留整理后的 case-study summary。原始 run logs、阶段性工作区和未公开研究材料不在此仓库中，因此这些历史数字用于说明测量校准过程，不作为可独立复现的当前 benchmark 结果。

- [Cold-start / CUDA Graph](cuda-graph-cold-start.md)
- [Chunk-size × Execution Mode](chunk-size-execution-mode.md)
- [Async Scheduling Reproduction](async-scheduling-reproduction.md)
- [Instrumentation Perturbation](instrumentation-perturbation.md)
