# 本地 LLM 推理环境搭建与验证

本文记录 RTX 5060 Laptop 上当前可工作的 LLM inference software stack。

## 1. 当前硬件

- GPU：NVIDIA RTX 5060 Laptop
- VRAM：8 GB
- Architecture：Blackwell
- Compute Capability：sm_120

## 2. 当前软件栈

| 组件 | 版本 |
| --- | --- |
| OS | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |

## 3. GPU 可见性

首先确认 WSL2 可以访问 GPU：

```bash
nvidia-smi
```

然后检查 PyTorch：

```bash
python - <<'PY'
import torch

print("torch:", torch.__version__)
print("torch cuda:", torch.version.cuda)
print("cuda available:", torch.cuda.is_available())

if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
    print("capability:", torch.cuda.get_device_capability(0))
PY
```

当前环境应识别到 RTX 5060 Laptop 与 compute capability 12.0。

## 4. CUDA Toolkit

检查：

```bash
nvcc --version
which nvcc
```

当前 toolkit 版本为 CUDA 13.0.3。

PyTorch CUDA runtime 与本地 CUDA Toolkit 是不同层次。对于普通预编译 kernel，PyTorch 自身的 CUDA runtime 可能已经足够；涉及 JIT / extension build 时，本地 toolkit、driver 和目标 GPU architecture 的兼容性会同时影响结果。

## 5. vLLM

检查：

```bash
python - <<'PY'
import vllm
print(vllm.__version__)
PY
```

当前主环境固定在 vLLM 0.26.0。

## 6. 最小模型验证

使用当前主要本地模型：

```bash
python examples/vllm-smoke-test.py --model Qwen/Qwen3-1.7B
```

该测试只验证最基础的完整推理链路：

```text
PyTorch CUDA
  → vLLM engine
  → model load
  → prefill
  → decode
  → output
```

能够完成输出后，才继续进行更具体的 profiling、runtime instrumentation 或研究实验。

## 7. 环境快照

```bash
python scripts/collect_environment.py
```

建议在修改 PyTorch、CUDA、vLLM 或模型版本后重新保存环境信息，以便定位 compatibility regression。
