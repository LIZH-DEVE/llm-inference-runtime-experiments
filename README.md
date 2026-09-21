# RTX 5060 Blackwell 本地 LLM 推理环境搭建与验证

本仓库记录在 **RTX 5060 Laptop 8GB（Blackwell, sm_120）** 上搭建本地 LLM 推理环境的完整过程，以及 PyTorch / CUDA / vLLM / 模型加载链路的实际验证结果。

重点不是整理通用的 LLM 理论，而是保留一套可以复查的本地推理环境：

```text
WSL2 Ubuntu
  → CUDA Toolkit
  → PyTorch CUDA
  → vLLM
  → local model load
  → inference smoke test
```

## 当前环境

| 组件 | 当前配置 |
| --- | --- |
| GPU | NVIDIA RTX 5060 Laptop，8 GB |
| GPU 架构 | Blackwell，sm_120 |
| 系统 | WSL2 Ubuntu |
| Python | 3.10.12 |
| PyTorch | 2.11.0 + cu130 |
| CUDA Toolkit | 13.0.3 |
| vLLM | 0.26.0 |

这套环境已经用于本地 LLM / VLM 推理、vLLM runtime 实验和 GPU compatibility 验证。

## 本地模型

目前本机实际使用或验证过的模型包括：

| 模型 | 本地用途 / 状态 |
| --- | --- |
| **Qwen/Qwen3-1.7B** | 当前主要 dense 模型；BF16 下用于 vLLM inference、runtime 与 state 实验 |
| **Qwen/Qwen3-VL-2B-Instruct** | 用于 VLM / visual encoder、multimodal runtime 与 CUDA Graph 相关实验 |
| **Qwen3.5-0.8B** | 用于早期 hybrid-model runtime / gate 实验 |
| **Qwen3.5-2B** | 用于本地 Qwen3.5 inference 与相关 runtime 实验 |
| **Qwen2.5-1.5B-Instruct** | 早期本地 vLLM 推理实验使用 |
| **Qwen2.5-3B** | 做过本地校准尝试；部分配置受 8 GB VRAM 限制出现 OOM |

详细记录见 [本地模型与用途](docs/local-models.md)。

## 环境验证

### 1. 检查 GPU / PyTorch / CUDA / vLLM

```bash
python scripts/collect_environment.py
```

脚本会输出：

- Python 版本；
- PyTorch 版本；
- PyTorch CUDA runtime；
- CUDA availability；
- GPU 型号；
- compute capability；
- VRAM；
- vLLM 版本。

### 2. 运行最小 vLLM 推理

```bash
python examples/vllm-smoke-test.py \
  --model Qwen/Qwen3-1.7B
```

验证链路：

```text
model load
  → request
  → prefill
  → decode
  → output
```

## 仓库结构

```text
.
├── README.md
├── docs/
│   ├── environment-setup.md
│   ├── local-models.md
│   └── troubleshooting/
│       └── wsl-cuda-vllm-checklist.md
├── examples/
│   └── vllm-smoke-test.py
└── scripts/
    └── collect_environment.py
```

## 文档

- [环境搭建与验证](docs/environment-setup.md)
- [本地模型与用途](docs/local-models.md)
- [WSL / CUDA / vLLM 排障清单](docs/troubleshooting/wsl-cuda-vllm-checklist.md)
