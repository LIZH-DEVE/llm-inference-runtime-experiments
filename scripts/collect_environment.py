#!/usr/bin/env python3
"""Print a compact environment snapshot for LLM runtime experiments."""

from __future__ import annotations

import platform
import sys


def main() -> None:
    print(f"python={sys.version.split()[0]}")
    print(f"platform={platform.platform()}")

    try:
        import torch
    except Exception as exc:  # diagnostic utility
        print(f"torch=unavailable ({exc})")
        return

    print(f"torch={torch.__version__}")
    print(f"torch_cuda={torch.version.cuda}")
    print(f"cuda_available={torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"gpu_count={torch.cuda.device_count()}")
        for idx in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(idx)
            total_gib = props.total_memory / (1024 ** 3)
            print(
                f"gpu[{idx}]={props.name}; "
                f"compute_capability={props.major}.{props.minor}; "
                f"vram_gib={total_gib:.2f}"
            )

    try:
        import vllm
        version = getattr(vllm, "__version__", "unknown")
        print(f"vllm={version}")
    except Exception as exc:  # diagnostic utility
        print(f"vllm=unavailable ({exc})")


if __name__ == "__main__":
    main()
