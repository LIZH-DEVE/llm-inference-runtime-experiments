#!/usr/bin/env python3
"""Summarize a numeric field from JSONL benchmark output.

Example:
    python scripts/summarize_latency.py run.jsonl --field ttft_ms
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("no values")

    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)

    if lo == hi:
        return ordered[lo]

    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    parser.add_argument("--field", required=True)
    args = parser.parse_args()

    values: list[float] = []

    with args.jsonl.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue

            row = json.loads(line)
            if args.field not in row:
                continue

            try:
                values.append(float(row[args.field]))
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"line {line_no}: field {args.field!r} is not numeric"
                ) from exc

    if not values:
        raise SystemExit(f"no numeric values found for field {args.field!r}")

    print(f"count={len(values)}")
    print(f"mean={statistics.fmean(values):.6f}")
    print(f"median={statistics.median(values):.6f}")
    print(f"p95={percentile(values, 0.95):.6f}")
    print(f"p99={percentile(values, 0.99):.6f}")
    print(f"min={min(values):.6f}")
    print(f"max={max(values):.6f}")


if __name__ == "__main__":
    main()
