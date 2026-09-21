#!/usr/bin/env python3
"""Minimal vLLM run with request-correlated scheduler tracing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from instrumentation.request_correlated_trace import JsonlRuntimeTrace
from instrumentation.vllm_scheduler_trace import (
    install_scheduler_trace,
    uninstall_scheduler_trace,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="Qwen/Qwen3-1.7B")
    parser.add_argument("--trace", default="results/scheduler-trace.jsonl")
    parser.add_argument("--max-model-len", type=int, default=2048)
    parser.add_argument("--max-tokens", type=int, default=16)
    args = parser.parse_args()

    trace = JsonlRuntimeTrace(args.trace)
    original_schedule = install_scheduler_trace(trace)

    try:
        from vllm import LLM, SamplingParams

        llm = LLM(
            model=args.model,
            dtype="bfloat16",
            max_model_len=args.max_model_len,
            gpu_memory_utilization=0.80,
        )
        params = SamplingParams(temperature=0.0, max_tokens=args.max_tokens)
        outputs = llm.generate(
            [
                "Explain KV cache in one sentence.",
                "Explain continuous batching in one sentence.",
            ],
            params,
        )

        for output in outputs:
            print(output.outputs[0].text.strip())
    finally:
        trace.close()
        uninstall_scheduler_trace(original_schedule)

    print(f"trace: {args.trace}")


if __name__ == "__main__":
    main()
