# 环境搭建与验证

本文记录当前用于本地 LLM inference runtime 学习与实验的环境基线，以及安装后需要完成的验证步骤。

## 1. 当前已验证环境

| 组件 | 配置 |
| --- | --- |
| GPU | NVIDIA RTX 5060 Laptop，8 GB |
| GPU 架构 | Blackwell，sm_120 |
| 系统 | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |
| 本地模型 | Qwen3-1.7B，BF16 |

这是一套已经实际运行过的环境基线，不代表所有 GPU / CUDA / vLLM 组合都应使用完全相同的版本。

## 2. WSL2 与 NVIDIA GPU

首先确认 WSL2 内可以访问 NVIDIA GPU：

```bash
nvidia-smi
```

需要确认：

- GPU 型号能够正常显示；
- driver 可见；
- WSL2 没有退回 CPU-only 环境。

## 3. Python 环境

建议单独建立 Python environment，避免系统 Python 与不同 CUDA / PyTorch 组合相互污染。

检查：

```bash
python --version
which python
```

当前基线使用 Python 3.10.12。

## 4. PyTorch 与 CUDA

安装完成后至少检查：

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

当前环境预期能够识别：

```text
RTX 5060 Laptop
compute capability 12.0
```

## 5. CUDA Toolkit

检查 CUDA compiler：

```bash
nvcc --version
which nvcc
```

当前使用 CUDA Toolkit 13.0.3。

PyTorch 自带 CUDA runtime 与系统安装的 CUDA Toolkit 是两个不同层次。遇到 JIT / extension build 问题时，需要同时检查：

- PyTorch 所使用的 CUDA 版本；
- 本地 `nvcc` 版本；
- driver 支持范围；
- extension / kernel 对 GPU architecture 的支持。

## 6. vLLM

检查 vLLM 是否可以被导入：

```bash
python - <<'PY'
import vllm
print(vllm.__version__)
PY
```

当前基线使用 vLLM 0.26.0。

随后运行：

```bash
python ../examples/vllm-smoke-test.py --model Qwen/Qwen3-1.7B
```

如果能够完成模型加载并产生输出，说明最基础的：

```text
PyTorch
→ CUDA
→ vLLM
→ model load
→ inference
```

链路已经打通。

## 7. 环境快照

仓库提供：

```bash
python scripts/collect_environment.py
```

建议在 benchmark 前保存环境快照，并同时记录：

- Git commit；
- model name / revision；
- dtype；
- max model length；
- vLLM flags；
- workload；
- warmup 次数；
- measured runs 数量。

这样后续结果才有可比较的上下文。
