#!/usr/bin/env python3
"""Summarize request-level metrics from streaming_benchmark.py JSONL."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path


def percentile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("empty metric")
    pos = (len(ordered) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return ordered[lo]
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def summarize(values: list[float]) -> dict[str, float]:
    return {
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "p95": percentile(values, 0.95),
        "p99": percentile(values, 0.99),
        "min": min(values),
        "max": max(values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", type=Path)
    args = parser.parse_args()

    rows = []
    run_summary = None

    with args.jsonl.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("record_type") == "request":
                rows.append(row)
            elif row.get("record_type") == "run_summary":
                run_summary = row

    successful = [row for row in rows if row.get("ok")]
    failed = len(rows) - len(successful)

    print(f"requests={len(rows)} successful={len(successful)} failed={failed}")
    if not successful:
        raise SystemExit("no successful requests")

    for field in ("ttft_ms", "tpot_ms", "e2e_ms"):
        values = [float(row[field]) for row in successful if row.get(field) is not None]
        stats = summarize(values)
        print(
            f"{field}: "
            f"mean={stats['mean']:.3f} "
            f"median={stats['median']:.3f} "
            f"p95={stats['p95']:.3f} "
            f"p99={stats['p99']:.3f} "
            f"min={stats['min']:.3f} "
            f"max={stats['max']:.3f}"
        )

    if run_summary:
        print(
            "run: "
            f"wall_s={float(run_summary['wall_s']):.3f} "
            f"request_s={float(run_summary['request_s']):.3f} "
            f"output_token_s={float(run_summary['output_token_s']):.3f}"
        )


if __name__ == "__main__":
    main()
