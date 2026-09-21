# Cold-start / CUDA Graph Artifact

## Initial Observation

早期一次实验中观察到约 **233.7%** 的表面性能差异。

如果只看第一次测量，很容易把它解释成稳定的 runtime performance gap。

## Control

重新设计实验：

- 将 model initialization 与 measured run 分离；
- 加入 warmup；
- 区分 CUDA Graph capture / compilation 与 steady-state；
- 只比较稳定阶段。

## Result

差异收缩到约 **9.9%**。

## Lesson

初始化、JIT 和 CUDA Graph capture 可以产生远大于 steady-state 差异的假信号。

因此在 LLM inference benchmark 中：

```text
first run
!=
steady-state performance
```

这一案例后来成为后续实验默认加入 warmup 与 cold-start separation 的原因。
