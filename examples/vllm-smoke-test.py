#!/usr/bin/env python3
"""Minimal offline vLLM smoke test.

This script checks that a model can be loaded and that one short request can
complete on the local GPU.
"""

from __future__ import annotations

import argparse

from vllm import LLM, SamplingParams


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-1.7B")
    parser.add_argument("--max-model-len", type=int, default=2048)
    parser.add_argument("--gpu-memory-utilization", type=float, default=0.80)
    parser.add_argument("--max-tokens", type=int, default=16)
    args = parser.parse_args()

    llm = LLM(
        model=args.model,
        dtype="bfloat16",
        max_model_len=args.max_model_len,
        gpu_memory_utilization=args.gpu_memory_utilization,
    )

    sampling_params = SamplingParams(
        temperature=0.0,
        max_tokens=args.max_tokens,
    )

    prompt = "Briefly explain what KV cache does in LLM inference."
    outputs = llm.generate([prompt], sampling_params)

    if not outputs or not outputs[0].outputs:
        raise RuntimeError("vLLM returned no output")

    text = outputs[0].outputs[0].text.strip()
    print("model:", args.model)
    print("prompt:", prompt)
    print("output:", text)


if __name__ == "__main__":
    main()
