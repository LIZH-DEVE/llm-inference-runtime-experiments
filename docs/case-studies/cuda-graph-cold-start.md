# Cold-start / CUDA Graph

## Environment

```text
GPU: RTX 5060 Laptop 8 GB
Model: Qwen2.5-3B
Runtime: historical vLLM 0.21.0-era experiment
```

## Initial Observation

初始测量中，相关配置出现约 **233.7%** 的表面差异。

## Control

重新组织测量后：

- 将 initialization 与 measured run 分离；
- 增加 warmup；
- 区分 CUDA Graph capture / compilation 与 steady-state；
- 只比较稳定运行阶段。

## Result

steady-state 差异收缩到约 **9.9%**。

## Takeaway

首轮运行混入 initialization、JIT 和 graph capture 后，结果可能远大于稳定运行阶段。

因此后续 benchmark 默认把：

```text
cold start
and
steady state
```

分开记录。
