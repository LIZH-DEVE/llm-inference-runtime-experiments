#!/usr/bin/env python3
"""Controlled streaming benchmark for a running vLLM OpenAI-compatible server.

Measures request-level TTFT, TPOT and end-to-end latency. The workload is
intentionally simple: fixed generation parameters, deterministic prompt
construction, explicit warmup, and bounded client concurrency.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from pathlib import Path
from typing import Any

import httpx


def make_prompt(index: int, repeat: int) -> str:
    body = "runtime " * max(repeat, 0)
    return (
        "Briefly explain one practical issue in LLM inference serving. "
        f"{body}request_id={index}"
    )


async def run_request(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    model: str,
    request_id: str,
    prompt: str,
    max_tokens: int,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "min_tokens": max_tokens,
        "temperature": 0.0,
        "ignore_eos": True,
        "stream": True,
        "return_token_ids": True,
        "request_id": request_id,
    }

    async with semaphore:
        start = time.perf_counter()
        first_token_at: float | None = None
        output_tokens = 0

        try:
            async with client.stream(
                "POST",
                f"{base_url.rstrip('/')}/v1/completions",
                json=payload,
                timeout=httpx.Timeout(1200.0),
            ) as response:
                if response.status_code != 200:
                    body = (await response.aread()).decode("utf-8", errors="replace")
                    return {
                        "record_type": "request",
                        "request_id": request_id,
                        "ok": False,
                        "status": response.status_code,
                        "error": body[:1000],
                    }

                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or not line.startswith("data:"):
                        continue

                    data = line[5:].strip()
                    if data == "[DONE]":
                        break

                    event = json.loads(data)
                    choice = (event.get("choices") or [{}])[0]
                    token_ids = choice.get("token_ids")

                    token_delta = 0
                    if isinstance(token_ids, list):
                        token_delta = len(token_ids)
                    elif choice.get("text"):
                        # Fallback for servers that omit the vLLM token-id extension.
                        token_delta = 1

                    if token_delta > 0 and first_token_at is None:
                        first_token_at = time.perf_counter()

                    output_tokens += token_delta

            end = time.perf_counter()
        except Exception as exc:
            return {
                "record_type": "request",
                "request_id": request_id,
                "ok": False,
                "error": repr(exc),
            }

    if first_token_at is None:
        return {
            "record_type": "request",
            "request_id": request_id,
            "ok": False,
            "error": "stream completed without an output token",
        }

    ttft_s = first_token_at - start
    e2e_s = end - start
    decode_s = max(end - first_token_at, 0.0)
    tpot_s = decode_s / max(output_tokens - 1, 1)

    return {
        "record_type": "request",
        "request_id": request_id,
        "ok": True,
        "output_tokens": output_tokens,
        "ttft_ms": ttft_s * 1000.0,
        "tpot_ms": tpot_s * 1000.0,
        "e2e_ms": e2e_s * 1000.0,
    }


async def main_async(args: argparse.Namespace) -> None:
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = {
        "record_type": "metadata",
        "model": args.model,
        "base_url": args.base_url,
        "warmup": args.warmup,
        "requests": args.requests,
        "concurrency": args.concurrency,
        "max_tokens": args.max_tokens,
        "prompt_repeat": args.prompt_repeat,
    }

    limits = httpx.Limits(
        max_connections=max(args.concurrency, 1) + 4,
        max_keepalive_connections=max(args.concurrency, 1) + 4,
    )

    async with httpx.AsyncClient(limits=limits) as client:
        warmup_sem = asyncio.Semaphore(1)
        for idx in range(args.warmup):
            result = await run_request(
                client,
                base_url=args.base_url,
                model=args.model,
                request_id=f"warmup-{idx}",
                prompt=make_prompt(idx, args.prompt_repeat),
                max_tokens=args.max_tokens,
                semaphore=warmup_sem,
            )
            if not result.get("ok"):
                raise RuntimeError(f"warmup failed: {result}")

        semaphore = asyncio.Semaphore(max(args.concurrency, 1))
        start = time.perf_counter()
        tasks = [
            run_request(
                client,
                base_url=args.base_url,
                model=args.model,
                request_id=f"measured-{idx}",
                prompt=make_prompt(idx, args.prompt_repeat),
                max_tokens=args.max_tokens,
                semaphore=semaphore,
            )
            for idx in range(args.requests)
        ]
        results = await asyncio.gather(*tasks)
        wall_s = time.perf_counter() - start

    successful = [row for row in results if row.get("ok")]
    total_output_tokens = sum(int(row.get("output_tokens", 0)) for row in successful)

    summary = {
        "record_type": "run_summary",
        "wall_s": wall_s,
        "successful_requests": len(successful),
        "failed_requests": len(results) - len(successful),
        "request_s": len(successful) / wall_s if wall_s > 0 else 0.0,
        "output_token_s": total_output_tokens / wall_s if wall_s > 0 else 0.0,
    }

    with output_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(metadata, ensure_ascii=False) + "\n")
        for row in results:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        fh.write(json.dumps(summary, ensure_ascii=False) + "\n")

    print(json.dumps(summary, indent=2))
    print(f"results: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", default="results/benchmark.jsonl")
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--requests", type=int, default=16)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--prompt-repeat", type=int, default=64)
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main_async(parse_args()))
