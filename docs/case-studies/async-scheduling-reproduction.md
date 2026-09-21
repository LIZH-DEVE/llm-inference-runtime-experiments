# Async Scheduling Reproduction

## Initial Observation

早期实验曾出现与 async scheduling 相关的明显 head-of-line blocking 信号。

## Reproduction Protocol

后续增加：

- 更充分的 warmup；
- 更多 measured repetitions；
- graceful server shutdown；
- timing / log 完整 flush；
- 更严格的 workload control。

## Result

原始信号没有稳定复现。

在加强控制后的测试中，关闭 async scheduling 在当时环境下反而更快；同时 GPU forward timing 也发生变化，因此无法把原始差异稳定归因到 scheduler HOL mechanism。

## Decision

停止围绕原解释继续优化。

## Lesson

一个 systems hypothesis 即使初始 magnitude 很大，也必须经过 controlled reproduction。

如果更严格实验不支持最初解释，应更新结论，而不是围绕第一次观察继续构建 optimization。
