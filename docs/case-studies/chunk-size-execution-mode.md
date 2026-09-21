# Chunk-size × Execution-mode Sensitivity

## Initial Observation

不同 chunk-size 配置最初表现出约 **30.9%** 的性能差异。

初步看来，chunk size 似乎对 runtime performance 很敏感。

## Control

后续重新运行时：

- 固定 model 与 workload；
- 控制 execution mode；
- 使用 eager 路径排除 CUDA Graph compilation / specialization 影响；
- 重复 measured runs。

## Result

原来的约 30.9% 差异收缩到约 **2.3%**。

## Lesson

参数敏感性实验不能只固定 scheduler 参数本身。

如果 execution mode 同时发生变化，观测到的性能差异可能主要来自：

- graph capture；
- compilation；
- shape specialization；
- eager / graph path 差异。

因此 scheduler experiment 与 GPU execution configuration 必须一起记录。
