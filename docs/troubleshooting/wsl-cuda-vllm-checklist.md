# WSL / CUDA / vLLM 排障清单

本清单用于排查本地 LLM inference 环境中最常见的基础问题。

## 1. WSL 看不到 GPU

先检查：

```bash
nvidia-smi
```

再检查：

```bash
python - <<'PY'
import torch
print(torch.cuda.is_available())
print(torch.version.cuda)
PY
```

如果 `nvidia-smi` 正常但 PyTorch 返回 `False`，优先检查 PyTorch 安装是否包含 CUDA 支持。

## 2. `nvcc` 不存在

检查：

```bash
which nvcc
nvcc --version
```

需要编译 CUDA extension / JIT kernel 时，本地 CUDA Toolkit 是否存在会变得重要。

只能够运行 PyTorch CUDA 并不等价于已经具备完整 CUDA Toolkit。

## 3. PyTorch CUDA 与 Toolkit 版本不同

检查：

```bash
python - <<'PY'
import torch
print(torch.__version__)
print(torch.version.cuda)
PY

nvcc --version
```

两者不一定完全相同，但 JIT / extension build 出错时需要同时记录。

## 4. 新 GPU 架构与 Kernel 支持

当前 RTX 5060 Laptop 属于 Blackwell，compute capability 为 sm_120。

如果出现：

- unsupported architecture；
- PTX toolchain incompatibility；
- kernel not available；
- JIT compile failure；

需要检查当前 PyTorch、CUDA Toolkit、vLLM 以及对应 attention / sampling kernel 是否支持目标 GPU architecture。

不要只通过修改一个 environment variable 就假设问题已经解决，应重新运行最小 smoke test 验证。

## 5. WSL Pin Memory

部分 WSL 环境下，pin memory 行为可能与原生 Linux 不同。

如果当前 vLLM 版本提供对应 WSL 开关，可在确认版本语义后测试：

```bash
export VLLM_WSL2_ENABLE_PIN_MEMORY=1
```

修改后应重新验证：

- engine initialization；
- request completion；
- memory usage；
- 是否出现新的 warning / error。

## 6. vLLM Import 成功但 Engine 启动失败

需要继续区分：

```text
Python import
≠
CUDA kernel 可用
≠
model load 成功
≠
完整 inference 成功
```

因此验证顺序建议为：

1. import vLLM；
2. 检查 PyTorch CUDA；
3. 加载最小模型；
4. 生成 1 个短输出；
5. 再进入 benchmark。

## 7. 保存错误上下文

排障记录至少保存：

- 完整 error message；
- PyTorch / CUDA / vLLM 版本；
- GPU 型号与 compute capability；
- 执行命令；
- 相关 environment variables；
- 修复前后验证结果。

这样后续升级版本时可以判断问题是否真正消失。
