# Benchmark Methodology

LLM inference benchmark 的核心不是“跑出一个数字”，而是确保不同结果具有可比较性。

## 1. 区分 Cold Start 与 Steady State

第一次运行可能包含：

- model initialization；
- JIT / kernel compilation；
- CUDA Graph capture；
- allocator growth；
- cache population。

如果目标是测量稳定运行性能，应先 warmup，再开始正式统计。

## 2. 固定实验条件

至少固定并记录：

- model / revision；
- dtype / quantization；
- input length；
- output length；
- batch / concurrency；
- max model length；
- GPU memory utilization；
- execution mode；
- CUDA Graph 是否启用；
- scheduler / cache 相关 flags。

否则不同 run 的数字很难直接比较。

## 3. 使用重复实验

单次 latency 很容易受到系统噪声影响。

建议至少观察：

- median；
- p95；
- p99；
- min / max；
- measured run 数量。

对于小幅性能差异，应先确认差异是否明显大于 run-to-run variance。

## 4. 同时观察多个指标

单看 throughput 可能掩盖 latency 退化，单看 latency 也可能忽略整体 GPU utilization。

常见组合包括：

- TTFT；
- TPOT；
- end-to-end latency；
- throughput；
- p95 / p99；
- GPU memory usage。

## 5. 注意 Execution Mode

Eager execution、CUDA Graph、JIT kernel 等执行方式可能显著改变结果。

因此对比某个 scheduler 或 runtime parameter 时，应确保 execution mode 一致；如果 execution mode 本身就是变量，则需要明确分组。

## 6. 检查 Profiling / Tracing 开销

Instrumentation 会改变被测系统。

加入 tracing 后，应检查：

- trace 是否显著增加 latency；
- 是否每 step 写入过多数据；
- 是否引入同步；
- 是否改变 request ordering。

必要时建立：

```text
instrumentation off
vs.
instrumentation on
```

的 overhead 对照。

## 7. 优先排除简单解释

遇到明显性能差异时，先检查：

- warmup 是否充分；
- cold-start 是否混入；
- model / prompt 是否真正一致；
- prefix-cache 是否命中；
- CUDA Graph 是否发生 capture；
- JIT compilation 是否发生；
- request ordering 是否改变；
- log flush / shutdown 是否影响结束时间。

## 8. 保存最小可复现信息

一个可复现实验至少应该能够回答：

```text
在哪台机器上？
什么软件版本？
什么模型？
什么 workload？
什么 flags？
warmup 几次？
测量几次？
统计的是什么指标？
```

仓库中的 `scripts/collect_environment.py` 用于记录环境，`scripts/summarize_latency.py` 用于做基础 latency 汇总。
