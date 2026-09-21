# Async Scheduling Reproduction

## Environment

```text
GPU: RTX 5060 Laptop 8 GB
Model: Qwen2.5-3B
Runtime: historical vLLM 0.21.0-era experiment
```

## Initial Observation

早期测量曾出现与 async scheduling 相关的明显 head-of-line blocking 信号。

## Reproduction

后续增加：

- warmup；
- measured repetitions；
- graceful server shutdown；
- timing / log 完整 flush；
- workload control。

## Result

原始信号没有稳定复现。

在加强控制后的测试中，关闭 async scheduling 在当时环境下反而更快；GPU forward timing 同时发生变化，因此原始差异不能稳定归因到 scheduler HOL。

## Takeaway

当更严格的 reproduction 改变结果方向时，应先停止 optimization，重新确认 execution path 和 attribution。
